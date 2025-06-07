from datetime import datetime, time
import csv
import pandas as pd

from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import ExtractHour
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import Event
from accounts.serializers import EventSerializer
from booking.models import Booking
from booking.serializers import BookingSerializer
from classroom.models import Block, Classroom
from timetable.models import Batch
from timetable.models import Timetable
from accounts.utils import is_admin

# --- API Views Only ---

class DashboardStatsView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        total_classrooms = Classroom.objects.count()
        empty_classrooms = Classroom.objects.filter(status='free').count()
        occupied_classrooms = Classroom.objects.filter(status='occupied').count()
        pending_bookings = Booking.objects.filter(status='pending').count()
        upcoming_events = Event.objects.filter(start_date__gte=timezone.now()) \
            .select_related('created_by').order_by('start_date')[:5]
        blocks = Block.objects.all()
        days = [choice[0] for choice in Timetable.DAY_CHOICES]
        return Response({
            'total_classrooms': total_classrooms,
            'empty_classrooms': empty_classrooms,
            'occupied_classrooms': occupied_classrooms,
            'pending_bookings': pending_bookings,
            'upcoming_events': EventSerializer(upcoming_events, many=True).data,
            'blocks': [{'id': b.id, 'name': b.name} for b in blocks],
            'days': days,
        })

class TimetableUploadView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
            required_columns = ['classroom', 'teacher', 'day', 'start_time', 'end_time']
            if not all(col in df.columns for col in required_columns):
                return Response({"error": "Missing required columns: must include 'classroom', 'teacher', 'day', 'start_time', 'end_time'"}, status=status.HTTP_400_BAD_REQUEST)
            errors, success_count = [], 0
            for idx, row in df.iterrows():
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
                        errors.append(f"Row {idx + 1}: Conflict for {row['classroom']} on {row['day']} from {row['start_time']} to {row['end_time']}")
                        continue
                    batch, _ = Batch.objects.get_or_create(
                        branch=row['branch'],
                        semester=row['semester'],
                        section=row.get('section', '')
                    )
                    Timetable.objects.create(
                        batch=batch,
                        classroom=classroom,
                        teacher=teacher,
                        day=row['day'],
                        start_time=start_time,
                        end_time=end_time,
                        subject_name=row.get('subject_name', '')
                    )
                    success_count += 1
                except Classroom.DoesNotExist:
                    errors.append(f"Row {idx + 1}: Classroom '{row['classroom']}' not found")
                except User.DoesNotExist:
                    errors.append(f"Row {idx + 1}: Teacher '{row['teacher']}' not found")
                except ValueError as e:
                    errors.append(f"Row {idx + 1}: Invalid time format for start_time or end_time - {str(e)}")
                except Exception as e:
                    errors.append(f"Row {idx + 1}: {str(e)}")
            if errors:
                return Response({"message": f"Partial success: {success_count} entries added", "errors": errors}, status=status.HTTP_207_MULTI_STATUS)
            return Response({"message": f"Success: {success_count} entries added"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": f"Failed to process file: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def all_timetables(request):
    entries = Timetable.objects.select_related('classroom', 'teacher').all()
    serializer = TimetableSerializer(entries, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def add_timetable(request):
    serializer = TimetableSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([AllowAny])
def update_timetable(request, pk):
    try:
        entry = Timetable.objects.get(pk=pk)
        serializer = TimetableSerializer(entry, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Timetable.DoesNotExist:
        return Response({'error': 'Timetable entry not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_timetable(request, pk):
    try:
        Timetable.objects.get(pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Timetable.DoesNotExist:
        return Response({'error': 'Timetable entry not found'}, status=status.HTTP_404_NOT_FOUND)

# --- CSRF-EXEMPTED DASHBOARD CHART VIEWS ---
@method_decorator(csrf_exempt, name='dispatch')
class UsageStatsView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        block = request.GET.get('block')
        day = request.GET.get('day')
        start_time_str = request.GET.get('start_time')
        end_time_str = request.GET.get('end_time')
        query = Timetable.objects.all()
        if block:
            query = query.filter(classroom__block__name=block)
        if day:
            query = query.filter(day=day)
        if start_time_str and end_time_str:
            try:
                start_time_val = time.fromisoformat(start_time_str)
                end_time_val = time.fromisoformat(end_time_str)
                query = query.filter(start_time__gte=start_time_val, end_time__lte=end_time_val)
            except ValueError:
                pass
        data = query.values('classroom__name').annotate(count=Count('id')).order_by('-count')
        return Response({
            'labels': [d['classroom__name'] for d in data],
            'data': [d['count'] for d in data]
        })

@method_decorator(csrf_exempt, name='dispatch')
class PeakHoursView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        block = request.GET.get('block')
        day = request.GET.get('day')
        start_time_str = request.GET.get('start_time')
        end_time_str = request.GET.get('end_time')
        query = Timetable.objects.annotate(hour=ExtractHour('start_time'))
        if block:
            query = query.filter(classroom__block__name=block)
        if day:
            query = query.filter(day=day)
        if start_time_str and end_time_str:
            try:
                start_time_val = time.fromisoformat(start_time_str)
                end_time_val = time.fromisoformat(end_time_str)
                query = query.filter(start_time__gte=start_time_val, end_time__lte=end_time_val)
            except ValueError:
                pass
        data = query.values('hour').annotate(count=Count('id')).order_by('hour')
        return Response({
            'labels': [f"{d['hour']}:00" for d in data],
            'data': [d['count'] for d in data]
        })

@method_decorator(csrf_exempt, name='dispatch')
class MostBookedClassroomsView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        block = request.GET.get('block')
        day = request.GET.get('day')
        start_time_str = request.GET.get('start_time')
        end_time_str = request.GET.get('end_time')
        bookings = Booking.objects.all()
        if block:
            bookings = bookings.filter(classroom__block__name=block)
        if day:
            bookings = bookings.filter(classroom__timetable__day=day)
        if start_time_str and end_time_str:
            try:
                start_time_val = time.fromisoformat(start_time_str)
                end_time_val = time.fromisoformat(end_time_str)
                bookings = bookings.filter(
                    classroom__timetable__start_time__gte=start_time_val,
                    classroom__timetable__end_time__lte=end_time_val
                )
            except ValueError:
                pass
        data = (bookings
                .values('classroom__name')
                .annotate(count=Count('id'))
                .order_by('-count')[:5])
        return Response({
            'labels': [d['classroom__name'] for d in data],
            'data': [d['count'] for d in data]
        })
class BookingListView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        bookings = Booking.objects.select_related('user', 'classroom').all()
        return Response(BookingSerializer(bookings, many=True).data)

class BookingDetailView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, pk):
        try:
            booking = Booking.objects.select_related('user', 'classroom').get(pk=pk)
            serializer = BookingSerializer(booking)
            return Response(serializer.data)
        except Booking.DoesNotExist:
            return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([AllowAny])
def approve_booking(request, pk):
    try:
        booking = Booking.objects.get(pk=pk)
        if booking.status != 'pending':
            return Response({'error': 'Booking is not in pending status'}, status=status.HTTP_400_BAD_REQUEST)
        booking.status = 'approved'
        booking.save()
        return Response({'message': 'Booking approved successfully'})
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([AllowAny])
def reject_booking(request, pk):
    try:
        booking = Booking.objects.get(pk=pk)
        if booking.status != 'pending':
            return Response({'error': 'Booking is not in pending status'}, status=status.HTTP_400_BAD_REQUEST)
        booking.status = 'rejected'
        booking.save()
        return Response({'message': 'Booking rejected successfully'})
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)

class EventListView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        events = Event.objects.select_related('created_by').all()
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def event_create_api(request):
    serializer = EventSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(created_by=request.user)
        return Response({'message': 'Event created successfully'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def available_classrooms(request):
    try:
        date = datetime.strptime(request.GET['date'], "%Y-%m-%d").date()
        start = datetime.strptime(request.GET['start_time'], "%H:%M").time()
        end = datetime.strptime(request.GET['end_time'], "%H:%M").time()
    except (KeyError, ValueError):
        return Response({'error': 'Invalid input: date (YYYY-MM-DD), start_time (HH:MM), and end_time (HH:MM) are required'}, status=status.HTTP_400_BAD_REQUEST)
    if start >= end:
        return Response({'error': 'End time must be after start time'}, status=status.HTTP_400_BAD_REQUEST)
    block = request.GET.get('block')
    day_name = date.strftime('%A')
    booked = Timetable.objects.filter(day=day_name, start_time__lt=end, end_time__gt=start)
    booked_ids = booked.values_list('classroom_id', flat=True)
    classrooms = Classroom.objects.exclude(id__in=booked_ids).select_related('block')
    if block:
        classrooms = classrooms.filter(block__name__icontains=block)
    return Response([{'id': c.id, 'name': c.name, 'block': c.block.name} for c in classrooms])

@api_view(['GET'])
@permission_classes([AllowAny])
def classroom_list(request):
    return Response([{'id': c.id, 'name': c.name} for c in Classroom.objects.all()])

@api_view(['GET'])
@permission_classes([AllowAny])
def teacher_list(request):
    users = User.objects.filter(is_staff=True)
    return Response([{'id': u.id, 'username': u.username} for u in users])

@api_view(['GET'])
@permission_classes([AllowAny])
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
@permission_classes([AllowAny])
def classroom_status(request):
    block = request.GET.get('block')
    day = request.GET.get('day', timezone.now().strftime('%A'))  # Default to today
    valid_days = [choice[0] for choice in Timetable.DAY_CHOICES]
    if day not in valid_days:
        return Response({'error': f"Invalid day: must be one of {valid_days}"}, status=status.HTTP_400_BAD_REQUEST)
    classrooms = Classroom.objects.all()
    if block:
        classrooms = classrooms.filter(block__name=block)
    current_time = timezone.now().time()
    date = timezone.now().date() if day == timezone.now().strftime('%A') else None
    occupied_bookings = 0
    if date:
        occupied_bookings = Booking.objects.filter(
            date=date,
            start_time__lte=current_time,
            end_time__gte=current_time,
            status='approved'
        ).count()
    occupied_timetables = Timetable.objects.filter(
        day=day,
        start_time__lte=current_time,
        end_time__gte=current_time
    ).count()
    total_occupied = occupied_bookings + occupied_timetables
    total_classrooms = classrooms.count()
    empty = max(total_classrooms - total_occupied, 0)
    return Response({'empty': empty, 'occupied': total_occupied})

