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
from timetable.models import Timetable
from classroom.models import Classroom
from booking.models import Booking

def is_admin(user):
    return user.is_staff or user.is_superuser

@user_passes_test(is_admin)
def admin_dashboard_view(request):
    return render(request, 'admin_dashboard/dashboard.html')

class TimetableUploadView(APIView):
    parser_classes = [MultiPartParser]
    
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
        
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
            errors = []
            success_count = 0

            for _, row in df.iterrows():
                try:
                    classroom = Classroom.objects.get(name=row['classroom'])
                    teacher = User.objects.get(username=row['teacher_username'])
                    Timetable.objects.create(
                        classroom=classroom,
                        teacher=teacher,
                        day=row['day'],
                        start_time=row['start_time'],
                        end_time=row['end_time']
                    )
                    success_count += 1
                except Classroom.DoesNotExist:
                    errors.append(f"Classroom '{row['classroom']}' not found")
                except User.DoesNotExist:
                    errors.append(f"Teacher '{row['teacher_username']}' not found")

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

    class Meta:
        model = Timetable
        fields = '__all__'
        extra_kwargs = {
            'start_time': {'format': '%H:%M'},
            'end_time': {'format': '%H:%M'}
        }

@api_view(['GET'])
def all_timetables(request):
    entries = Timetable.objects.select_related('classroom', 'teacher').all()
    serializer = TimetableSerializer(entries, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def add_timetable(request):
    serializer = TimetableSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
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
def delete_timetable(request, pk):
    try:
        entry = Timetable.objects.get(pk=pk)
        entry.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Timetable.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

class UsageStatsView(APIView):
    def get(self, request):
        usage_data = Timetable.objects.values('classroom__name').annotate(
            count=Count('classroom')
        ).order_by('-count')
        return Response({
            'labels': [item['classroom__name'] for item in usage_data],
            'data': [item['count'] for item in usage_data]
        })

class PeakHoursView(APIView):
    def get(self, request):
        data = Timetable.objects.annotate(hour=ExtractHour('start_time')) \
            .values('hour').annotate(count=Count('id')).order_by('hour')
        return Response({
            'labels': [f"{entry['hour']}:00" for entry in data],
            'data': [entry['count'] for entry in data]
        })

class ActiveFacultyView(APIView):
    def get(self, request):
        data = Timetable.objects.values('teacher__username') \
            .annotate(count=Count('id')).order_by('-count')
        return Response({
            'labels': [entry['teacher__username'] for entry in data],
            'data': [entry['count'] for entry in data]
        })

class PendingBookingsView(APIView):
    def get(self, request):
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
    try:
        booking = Booking.objects.get(id=booking_id)
        booking.status = 'approved'
        booking.save()
        return Response({'message': 'Booking approved'})
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def reject_booking(request, booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
        booking.status = 'rejected'
        booking.save()
        return Response({'message': 'Booking rejected'})
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def available_classrooms(request):
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
    data = [{'id': c.id, 'name': c.name} for c in Classroom.objects.all()]
    return Response(data)

@api_view(['GET'])
def teacher_list(request):
    users = User.objects.filter(is_staff=True)
    data = [{'id': u.id, 'username': u.username} for u in users]
    return Response(data)

@api_view(['GET'])
def export_timetable_csv(request):
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
