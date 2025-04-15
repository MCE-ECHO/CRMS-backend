import pandas as pd
import csv
from datetime import datetime
from django.db.models import Count
from django.db.models.functions import ExtractHour
from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import user_passes_test
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import serializers, status
from timetable.models import Timetable
from classroom.models import Classroom
from booking.models import Booking
from .forms import UploadFileForm

# Constants for error messages
ERROR_AUTH_REQUIRED = {"error": "Authentication required"}
ERROR_NO_FILE_UPLOADED = {"error": "No file uploaded"}
ERROR_FILE_NOT_FOUND = {"error": "File not found"}
ERROR_EMPTY_FILE = {"error": "Uploaded file is empty"}
ERROR_INVALID_FILE = {"error": "Error parsing the file. Make sure it's a valid CSV or Excel file."}

# Utility Functions
def is_admin(user):
    """Check if the user is an admin."""
    return user.is_staff or user.is_superuser

# Admin Dashboard View
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    """Render the admin dashboard."""
    return render(request, 'admin_dashboard/dashboard.html')

# Timetable Upload View
class TimetableUploadView(APIView):
    parser_classes = [MultiPartParser]
    
    def post(self, request, *args, **kwargs):
        """Upload and process a timetable file."""
        if not request.user.is_authenticated:
            return Response(ERROR_AUTH_REQUIRED, status=status.HTTP_401_UNAUTHORIZED)
        
        file = request.FILES.get('file')
        if not file:
            return Response(ERROR_NO_FILE_UPLOADED, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Read Excel if the file ends with .xlsx, otherwise CSV
            df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
            errors = []
            success_count = 0

            # Determine which columns to use for classroom and teacher
            classroom_field = 'classroom_name' if 'classroom_name' in df.columns else 'classroom'
            teacher_field = 'teacher_name' if 'teacher_name' in df.columns else 'teacher'

            for _, row in df.iterrows():
                try:
                    # Get the Classroom and Teacher using detected column names
                    classroom = Classroom.objects.get(name=row[classroom_field])
                    teacher = User.objects.get(username=row[teacher_field])
                    
                    # Parse start and end times; expecting HH:MM format
                    start_time = datetime.strptime(row['start_time'], '%H:%M').time()
                    end_time = datetime.strptime(row['end_time'], '%H:%M').time()
                    
                    # Create Timetable entry; include subject_name and block_name if provided
                    Timetable.objects.create(
                        classroom=classroom,
                        teacher=teacher,
                        day=row['day'],
                        start_time=start_time,
                        end_time=end_time,
                        subject_name=row.get('subject_name', ''),
                        block_name=row.get('block_name', '')
                    )
                    success_count += 1
                except Classroom.DoesNotExist:
                    errors.append(f"Classroom '{row.get(classroom_field)}' not found")
                except User.DoesNotExist:
                    errors.append(f"Teacher '{row.get(teacher_field)}' not found")
                except ValueError as ve:
                    errors.append(f"Invalid time format for classroom {row.get(classroom_field)}: {ve}")
                except Exception as e:
                    errors.append(f"Error processing row: {e}")

            if errors:
                return Response({
                    "message": f"Partial success: {success_count} entries added",
                    "errors": errors
                }, status=status.HTTP_207_MULTI_STATUS)
                
            return Response({"message": f"{success_count} entries added successfully"},
                            status=status.HTTP_201_CREATED)

        except FileNotFoundError:
            return Response(ERROR_FILE_NOT_FOUND, status=status.HTTP_400_BAD_REQUEST)
        except pd.errors.EmptyDataError:
            return Response(ERROR_EMPTY_FILE, status=status.HTTP_400_BAD_REQUEST)
        except pd.errors.ParserError:
            return Response(ERROR_INVALID_FILE, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Timetable Serializer
class TimetableSerializer(serializers.ModelSerializer):
    """Serializer for Timetable model."""
    classroom = serializers.PrimaryKeyRelatedField(queryset=Classroom.objects.all())
    teacher = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(is_staff=True))
    start_time = serializers.TimeField(format='%H:%M')
    end_time = serializers.TimeField(format='%H:%M')

    class Meta:
        model = Timetable
        fields = '__all__'

# Timetable CRUD Endpoints
@api_view(['GET'])
def all_timetables(request):
    """Fetch all timetables."""
    entries = Timetable.objects.select_related('classroom', 'teacher').all()
    serializer = TimetableSerializer(entries, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def add_timetable(request):
    """Add a new timetable entry."""
    serializer = TimetableSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_timetable(request, pk):
    """Update a timetable entry."""
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
def delete_timetable(request, pk):
    """Delete a timetable entry."""
    try:
        entry = Timetable.objects.get(pk=pk)
        entry.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Timetable.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

# Statistics and Utility APIViews
class UsageStatsView(APIView):
    def get(self, request):
        """Fetch classroom usage statistics."""
        usage_data = Timetable.objects.values('classroom__name').annotate(
            count=Count('classroom')
        ).order_by('-count')
        return Response({
            'labels': [item['classroom__name'] for item in usage_data],
            'data': [item['count'] for item in usage_data]
        })

class PeakHoursView(APIView):
    def get(self, request):
        """Fetch peak hours data."""
        data = Timetable.objects.annotate(hour=ExtractHour('start_time')) \
            .values('hour').annotate(count=Count('id')).order_by('hour')
        return Response({
            'labels': [f"{entry['hour']}:00" for entry in data],
            'data': [entry['count'] for entry in data]
        })

class ActiveFacultyView(APIView):
    def get(self, request):
        """Fetch active faculty data."""
        data = Timetable.objects.values('teacher__username') \
            .annotate(count=Count('id')).order_by('-count')
        return Response({
            'labels': [entry['teacher__username'] for entry in data],
            'data': [entry['count'] for entry in data]
        })

class PendingBookingsView(APIView):
    def get(self, request):
        """Fetch pending bookings."""
        pending = Booking.objects.filter(status='pending').select_related('classroom', 'user')
        data = [{
            'id': b.id,
            'user': b.user.username,
            'classroom': b.classroom.name,
            'date': b.date,
            'start_time': b.start_time.strftime('%H:%M'),
            'end_time': b.end_time.strftime('%H:%M'),
        } for b in pending]
        return Response(data)

@api_view(['POST'])
def approve_booking(request, booking_id):
    """Approve a booking."""
    try:
        booking = Booking.objects.get(id=booking_id)
        booking.status = 'approved'
        booking.save()
        return Response({'message': 'Booking approved'})
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def reject_booking(request, booking_id):
    """Reject a booking."""
    try:
        booking = Booking.objects.get(id=booking_id)
        booking.status = 'rejected'
        booking.save()
        return Response({'message': 'Booking rejected'})
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def available_classrooms(request):
    """Fetch available classrooms."""
    date = request.GET.get('date')
    start = request.GET.get('start_time')
    end = request.GET.get('end_time')
    block = request.GET.get('block')

    try:
        start_time = datetime.strptime(start, "%H:%M").time()
        end_time = datetime.strptime(end, "%H:%M").time()
    except (ValueError, TypeError):
        return Response({'error': 'Invalid time format'}, status=status.HTTP_400_BAD_REQUEST)

    booked_ids = Booking.objects.filter(
        date=date,
        start_time__lt=end_time,
        end_time__gt=start_time,
        status='approved'
    ).values_list('classroom_id', flat=True)

    classrooms = Classroom.objects.exclude(id__in=booked_ids)
    if block:
        classrooms = classrooms.filter(block__icontains=block)

    return Response([{'name': c.name, 'block': c.block} for c in classrooms])

@api_view(['GET'])
def classroom_list(request):
    """Fetch list of classrooms."""
    data = [{'id': c.id, 'name': c.name} for c in Classroom.objects.all()]
    return Response(data)

@api_view(['GET'])
def teacher_list(request):
    """Fetch list of teachers."""
    users = User.objects.filter(is_staff=True)
    data = [{'id': u.id, 'username': u.username} for u in users]
    return Response(data)

@api_view(['GET'])
def export_timetable_csv(request):
    """Export timetable as CSV."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="timetable_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Day', 'Start Time', 'End Time', 'Classroom', 'Teacher'])
    
    try:
        for row in Timetable.objects.select_related('classroom', 'teacher'):
            writer.writerow([
                row.day,
                row.start_time.strftime('%H:%M'),
                row.end_time.strftime('%H:%M'),
                row.classroom.name,
                row.teacher.username
            ])
        return response
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

