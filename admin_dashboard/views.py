import pandas as pd
import csv
from datetime import datetime
from django.db.models import Count
from django.db.models.functions import ExtractHour
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import serializers, status
from rest_framework.permissions import IsAdminUser

from timetable.models import Timetable
from classroom.models import Classroom
from booking.models import Booking
from booking.serializers import BookingSerializer
from .forms import UploadFileForm
from accounts.utils import is_admin

@user_passes_test(is_admin)
def admin_dashboard_view(request):
    # Admin dashboard main view
    return render(request, 'admin_dashboard/dashboard.html')

class TimetableUploadView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        # Handle timetable file upload
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if file.name.endswith('.xlsx'):
                df = pd.read_excel(file)
            elif file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                return Response({"error": "Unsupported file format"}, status=status.HTTP_400_BAD_REQUEST)

            required_columns = ['classroom', 'teacher', 'day', 'start_time', 'end_time']
            if not all(col in df.columns for col in required_columns):
                return Response({"error": "Missing required columns"}, status=status.HTTP_400_BAD_REQUEST)

            errors = []
            success_count = 0

            for _, row in df.iterrows():
                try:
                    classroom = Classroom.objects.get(name=row['classroom'])
                    teacher = User.objects.get(username=row['teacher'])
                    start_time = datetime.strptime(row['start_time'], '%H:%M').time()
                    end_time = datetime.strptime(row['end_time'], '%H:%M').time()

                    conflicts = Timetable.objects.filter(
                        classroom=classroom,
                        day=row['day'],
                        start_time__lt=end_time,
                        end_time__gt=start_time
                    )
                    if conflicts.exists():
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
                except ValueError as ve:
                    errors.append(f"Invalid time format for {row['classroom']}: {ve}")
                except Exception as e:
                    errors.append(f"Error processing row: {e}")

            if errors:
                return Response({
                    "message": f"Partial success: {success_count} entries added",
                    "errors": errors
                }, status=status.HTTP_207_MULTI_STATUS)

            return Response({"message": f"{success_count} entries added successfully"},
                            status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TimetableSerializer(serializers.ModelSerializer):
    classroom = serializers.PrimaryKeyRelatedField(queryset=Classroom.objects.all())
    teacher = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(is_staff=True))
    start_time = serializers.TimeField(format='%H:%M')
    end_time = serializers.TimeField(format='%H:%M')

    class Meta:
        model = Timetable
        fields = '__all__'

@api_view(['GET'])
@user_passes_test(is_admin)
def all_timetables(request):
    # Retrieve all timetable entries
    entries = Timetable.objects.select_related('classroom', 'teacher').all()
    serializer = TimetableSerializer(entries, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@user_passes_test(is_admin)
def add_timetable(request):
    # Add a new timetable entry
    serializer = TimetableSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@user_passes_test(is_admin)
def update_timetable(request, pk):
    # Update an existing timetable entry
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
    # Delete a timetable entry
    try:
        entry = Timetable.objects.get(pk=pk)
        entry.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Timetable.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

class UsageStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        # Classroom usage statistics
        usage_data = Timetable.objects.values('classroom__name').annotate(
            count=Count('classroom')
        ).order_by('-count')
        return Response({
            'labels': [item['classroom__name'] for item in usage_data],
            'data': [item['count'] for item in usage_data]
        })

class PeakHoursView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        # Peak usage hours statistics
        data = Timetable.objects.annotate(hour=ExtractHour('start_time')) \
            .values('hour').annotate(count=Count('id')).order_by('hour')
        return Response({
            'labels': [f"{entry['hour']}:00" for entry in data],
            'data': [entry['count'] for entry in data]
        })

class ActiveFacultyView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        # Faculty activity statistics
        data = Timetable.objects.values('teacher__username') \
            .annotate(count=Count('id')).order_by('-count')
        return Response({
            'labels': [entry['teacher__username'] for entry in data],
            'data': [entry['count'] for entry in data]
        })

@api_view(['GET'])
@user_passes_test(is_admin)
def available_classrooms(request):
    # Check available classrooms
    date = request.GET.get('date')
    start = request.GET.get('start_time')
    end = request.GET.get('end_time')
    block = request.GET.get('block')

    try:
        start_time = datetime.strptime(start, "%H:%M").time()
        end_time = datetime.strptime(end, "%H:%M").time()
        search_date = datetime.strptime(date, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return Response({'error': 'Invalid time/date format'}, status=status.HTTP_400_BAD_REQUEST)

    booked_ids = Timetable.objects.filter(
        day=search_date.strftime('%A'),
        start_time__lt=end_time,
        end_time__gt=start_time
    ).values_list('classroom_id', flat=True)

    classrooms = Classroom.objects.exclude(id__in=booked_ids).select_related('block')
    if block:
        classrooms = classrooms.filter(block__name__icontains=block)

    return Response([{'name': c.name, 'block': c.block.name} for c in classrooms])

@api_view(['GET'])
@user_passes_test(is_admin)
def classroom_list(request):
    # List all classrooms
    data = [{'id': c.id, 'name': c.name} for c in Classroom.objects.all()]
    return Response(data)

@api_view(['GET'])
@user_passes_test(is_admin)
def teacher_list(request):
    # List all teachers
    users = User.objects.filter(is_staff=True)
    data = [{'id': u.id, 'username': u.username} for u in users]
    return Response(data)

@api_view(['GET'])
@user_passes_test(is_admin)
def export_timetable_csv(request):
    # Export timetable as CSV
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

class BookingListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        # List all bookings for admin review
        bookings = Booking.objects.all().select_related('user', 'classroom')
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

@api_view(['POST'])
@user_passes_test(is_admin)
def approve_booking(request, pk):
    # Approve a booking
    try:
        booking = Booking.objects.get(pk=pk)
        booking.status = 'approved'
        booking.save()
        return Response({'message': 'Booking approved'}, status=status.HTTP_200_OK)
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@user_passes_test(is_admin)
def reject_booking(request, pk):
    # Reject a booking
    try:
        booking = Booking.objects.get(pk=pk)
        booking.status = 'rejected'
        booking.save()
        return Response({'message': 'Booking rejected'}, status=status.HTTP_200_OK)
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
