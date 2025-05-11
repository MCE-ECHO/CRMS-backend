from datetime import datetime
import csv
import pandas as pd
import json
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models.functions import ExtractHour
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.decorators import api_view
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.models import Event
from accounts.utils import is_admin
from booking.models import Booking
from booking.serializers import BookingSerializer
from classroom.models import Block, Classroom
from timetable.models import Timetable
from .forms import EventForm

@user_passes_test(is_admin)
def admin_dashboard_view(request):
    total_classrooms = Classroom.objects.count()
    empty_classrooms = Classroom.objects.filter(status='free').count()
    occupied_classrooms = Classroom.objects.filter(status='occupied').count()
    pending_bookings = Booking.objects.filter(status='pending').count()
    upcoming_events = Event.objects.filter(start_date__gte=datetime.now()).order_by('start_date')[:5]
    blocks = Block.objects.all()
    days = [choice[0] for choice in Timetable.DAY_CHOICES]
    context = {
        'total_classrooms': total_classrooms,
        'empty_classrooms': empty_classrooms,
        'occupied_classrooms': occupied_classrooms,
        'pending_bookings': pending_bookings,
        'upcoming_events': upcoming_events,
        'blocks': blocks,
        'days': days,
    }
    return render(request, 'admin_dashboard/dashboard.html', context)

@user_passes_test(is_admin)
def upload_timetable(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        if file and file.name.endswith(('.csv', '.xlsx')):
            request.FILES['file'] = file
            response = TimetableUploadView.as_view()(request)
            if response.status_code == status.HTTP_201_CREATED:
                messages.success(request, response.data['message'])
            elif response.status_code == status.HTTP_207_MULTI_STATUS:
                messages.warning(request, f"{response.data['message']}. Errors: {'; '.join(response.data['errors'])}")
            else:
                messages.error(request, response.data.get('error', 'Upload failed.'))
        else:
            messages.error(request, 'Please upload a valid CSV or Excel file.')
        return redirect('admin_dashboard:admin-dashboard')
    return redirect('admin_dashboard:admin-dashboard')

@user_passes_test(is_admin)
def timetable_management(request):
    timetables = Timetable.objects.select_related('classroom', 'teacher').all()
    block = request.GET.get('block')
    classroom = request.GET.get('classroom')
    day = request.GET.get('day')
    if block:
        timetables = timetables.filter(classroom__block__name__icontains=block)
    if classroom:
        timetables = timetables.filter(classroom__name__icontains=classroom)
    if day:
        timetables = timetables.filter(day=day)
    context = {
        'timetables': timetables,
        'blocks': Block.objects.all(),
        'classrooms': Classroom.objects.all(),
        'days': [choice[0] for choice in Timetable.DAY_CHOICES],
    }
    return render(request, 'admin_dashboard/timetable_management.html', context)

@user_passes_test(is_admin)
def booking_management(request):
    bookings = Booking.objects.select_related('user', 'classroom').all()
    return render(request, 'admin_dashboard/booking_management.html', {'bookings': bookings})

@user_passes_test(is_admin)
def event_management(request):
    events = Event.objects.all()
    return render(request, 'admin_dashboard/event_management.html', {'events': events})

@user_passes_test(is_admin)
def event_create_view(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, 'Event created successfully.')
            return redirect('admin_dashboard:event-management')
    else:
        form = EventForm()
    return render(request, 'admin_dashboard/event_create.html', {'form': form})

@user_passes_test(is_admin)
def event_list_view(request):
    events = Event.objects.all()
    return render(request, 'admin_dashboard/event_list.html', {'events': events})

@user_passes_test(is_admin)
def empty_classrooms_view(request):
    classrooms = Classroom.objects.filter(status='free')
    return render(request, 'admin_dashboard/classroom_list.html', {'classrooms': classrooms, 'title': 'Empty Classrooms'})

@user_passes_test(is_admin)
def occupied_classrooms_view(request):
    classrooms = Classroom.objects.filter(status='occupied')
    return render(request, 'admin_dashboard/classroom_list.html', {'classrooms': classrooms, 'title': 'Occupied Classrooms'})

class TimetableSerializer(serializers.ModelSerializer):
    classroom = serializers.PrimaryKeyRelatedField(queryset=Classroom.objects.all())
    teacher = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(is_staff=True))
    class Meta:
        model = Timetable
        fields = '__all__'

class TimetableUploadView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
            required_columns = ['classroom', 'teacher', 'day', 'start_time', 'end_time']
            if not all(col in df.columns for col in required_columns):
                return Response({"error": "Missing required columns"}, status=status.HTTP_400_BAD_REQUEST)
            errors, success_count = [], 0
            for _, row in df.iterrows():
                try:
                    classroom = Classroom.objects.get(name=row['classroom'])
                    teacher = User.objects.get(username=row['teacher'])
                    start_time = datetime.strptime(row['start_time'], '%H:%M').time()
                    end_time = datetime.strptime(row['end_time'], '%H:%M').time()
                    conflict = Timetable.objects.filter(
                        classroom=classroom,
                        day=row['day'],
                        start_time__lt=end_time,
                        end_time__gt=start_time
                    )
                    if conflict.exists():
                        errors.append(f"Conflict for {row['classroom']} on {row['day']} at {row['start_time']}")
                        continue
                    Timetable.objects.create(
                        classroom=classroom,
                        teacher=teacher,
                        day=row['day'],
                        start_time=start_time,
                        end_time=end_time,
                        subject_name=row.get('subject_name', '')
                    )
                    success_count += 1
                except Classroom.DoesNotExist:
                    errors.append(f"Classroom '{row['classroom']}' not found")
                except User.DoesNotExist:
                    errors.append(f"Teacher '{row['teacher']}' not found")
                except Exception as e:
                    errors.append(str(e))
            if errors:
                return Response({"message": f"Partial success: {success_count} added", "errors": errors}, status=status.HTTP_207_MULTI_STATUS)
            return Response({"message": f"{success_count} entries added"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@user_passes_test(is_admin)
def all_timetables(request):
    entries = Timetable.objects.select_related('classroom', 'teacher').all()
    return Response(TimetableSerializer(entries, many=True).data)

@api_view(['POST'])
@user_passes_test(is_admin)
def add_timetable(request):
    serializer = TimetableSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@user_passes_test(is_admin)
def update_timetable(request, pk):
    try:
        entry = Timetable.objects.get(pk=pk)
        serializer = TimetableSerializer(entry, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Timetable.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@user_passes_test(is_admin)
def delete_timetable(request, pk):
    try:
        Timetable.objects.get(pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Timetable.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

class UsageStatsView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        block_id = request.GET.get('block')
        day = request.GET.get('day')
        query = Timetable.objects
        if block_id:
            query = query.filter(classroom__block_id=block_id)
        if day:
            query = query.filter(day=day)
        data = query.values('classroom__name').annotate(count=Count('id')).order_by('-count')
        return Response({
            'labels': [d['classroom__name'] for d in data],
            'data': [d['count'] for d in data]
        })

class PeakHoursView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        day = request.GET.get('day')
        query = Timetable.objects.annotate(hour=ExtractHour('start_time')).values('hour').annotate(count=Count('id')).order_by('hour')
        if day:
            query = query.filter(day=day)
        data = query
        return Response({
            'labels': [f"{d['hour']}:00" for d in data],
            'data': [d['count'] for d in data]
        })

class ActiveFacultyView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        block_id = request.GET.get('block')
        query = Timetable.objects
        if block_id:
            query = query.filter(classroom__block_id=block_id)
        data = query.values('teacher__username').annotate(count=Count('id')).order_by('-count')
        return Response({
            'labels': [d['teacher__username'] for d in data],
            'data': [d['count'] for d in data]
        })

class BookingListView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        bookings = Booking.objects.select_related('user', 'classroom').all()
        return Response(BookingSerializer(bookings, many=True).data)

@api_view(['POST'])
@user_passes_test(is_admin)
def approve_booking(request, pk):
    try:
        booking = Booking.objects.get(pk=pk)
        booking.status = 'approved'
        booking.save()
        return Response({'message': 'Booking approved'})
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@user_passes_test(is_admin)
def reject_booking(request, pk):
    try:
        booking = Booking.objects.get(pk=pk)
        booking.status = 'rejected'
        booking.save()
        return Response({'message': 'Booking rejected'})
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@user_passes_test(is_admin)
def available_classrooms(request):
    try:
        date = datetime.strptime(request.GET['date'], "%Y-%m-%d").date()
        start = datetime.strptime(request.GET['start_time'], "%H:%M").time()
        end = datetime.strptime(request.GET['end_time'], "%H:%M").time()
    except (KeyError, ValueError):
        return Response({'error': 'Invalid input'}, status=status.HTTP_400_BAD_REQUEST)
    block = request.GET.get('block')
    day_name = date.strftime('%A')
    booked = Timetable.objects.filter(day=day_name, start_time__lt=end, end_time__gt=start)
    booked_ids = booked.values_list('classroom_id', flat=True)
    classrooms = Classroom.objects.exclude(id__in=booked_ids).select_related('block')
    if block:
        classrooms = classrooms.filter(block__name__icontains=block)
    return Response([{'id': c.id, 'name': c.name, 'block': c.block.name} for c in classrooms])

@api_view(['GET'])
@user_passes_test(is_admin)
def classroom_list(request):
    return Response([{'id': c.id, 'name': c.name} for c in Classroom.objects.all()])

@api_view(['GET'])
@user_passes_test(is_admin)
def teacher_list(request):
    users = User.objects.filter(is_staff=True)
    return Response([{'id': u.id, 'username': u.username} for u in users])

@api_view(['GET'])
@user_passes_test(is_admin)
def export_timetable_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="timetable_export.csv"'
    writer = csv.writer(response)
    writer.writerow(['Day', 'Start Time', 'End Time', 'Classroom', 'Teacher', 'Subject'])
    for row in Timetable.objects.select_related('classroom', 'teacher'):
        writer.writerow([
            row.day,
            row.start_time.strftime('%H:%M'),
            row.end_time.strftime('%H:%M'),
            row.classroom.name,
            row.teacher.username if row.teacher else 'N/A',
            row.subject_name or 'N/A'
        ])
    return response

@api_view(['GET'])
@user_passes_test(is_admin)
def classroom_status(request):
    block = request.GET.get('block')
    day = request.GET.get('day', timezone.now().strftime('%A'))  # Default to today
    classrooms = Classroom.objects.all()
    if block:
        classrooms = classrooms.filter(block__name=block)
    
    current_time = timezone.now().time()
    date = timezone.now().date()
    
    occupied = Booking.objects.filter(
        date=date,
        start_time__lte=current_time,
        end_time__gte=current_time,
        status='approved'
    ).count()
    
    empty = classrooms.count() - occupied
    return Response({'empty': empty, 'occupied': occupied})
