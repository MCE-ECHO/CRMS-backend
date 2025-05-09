import pandas as pd
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from .models import Timetable
from .serializers import TimetableSerializer
from classroom.models import Classroom, Block
from django.contrib.auth.models import User
from accounts.utils import is_admin
from django import forms

class TimetableForm(forms.ModelForm):
    class Meta:
        model = Timetable
        fields = ['classroom', 'teacher', 'day', 'start_time', 'end_time', 'subject_name']
        widgets = {
            'classroom': forms.Select(attrs={'class': 'w-full p-3 border rounded-lg'}),
            'teacher': forms.Select(attrs={'class': 'w-full p-3 border rounded-lg'}),
            'day': forms.Select(attrs={'class': 'w-full p-3 border rounded-lg'}),
            'start_time': forms.TimeInput(attrs={'class': 'w-full p-3 border rounded-lg', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'w-full p-3 border rounded-lg', 'type': 'time'}),
            'subject_name': forms.TextInput(attrs={'class': 'w-full p-3 border rounded-lg'}),
        }

@user_passes_test(is_admin)
def timetable_create_view(request):
    if request.method == 'POST':
        form = TimetableForm(request.POST)
        if form.is_valid():
            timetable = form.save(commit=False)
            conflicts = Timetable.objects.filter(
                classroom=timetable.classroom,
                day=timetable.day,
                start_time__lt=timetable.end_time,
                end_time__gt=timetable.start_time
            )
            if conflicts.exists():
                messages.error(request, 'This classroom is already scheduled for the selected time.')
            else:
                timetable.save()
                messages.success(request, 'Timetable entry created successfully.')
                return redirect('admin_dashboard:timetable-management')
        else:
            messages.error(request, 'Error creating timetable entry.')
    else:
        form = TimetableForm()
    return render(request, 'timetable/timetable_form.html', {'form': form})

@login_required
def timetable_list_view(request):
    block_id = request.GET.get('block')
    timetables = Timetable.objects.all().select_related('classroom__block', 'teacher')
    blocks = Block.objects.all()
    if block_id:
        timetables = timetables.filter(classroom__block_id=block_id)
    return render(request, 'timetable/timetable_list.html', {
        'timetables': timetables,
        'blocks': blocks,
        'selected_block': block_id
    })

class TimetableUploadView(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            df = pd.read_excel(file) if file.name.endswith('.xlsx') else pd.read_csv(file)
            required = ['classroom', 'teacher', 'day', 'start_time', 'end_time']
            if not all(col in df.columns for col in required):
                return Response({"error": "Missing required columns"}, status=status.HTTP_400_BAD_REQUEST)

            errors = []
            success_count = 0

            for _, row in df.iterrows():
                try:
                    classroom = Classroom.objects.get(name=row['classroom'])
                    teacher = User.objects.get(username=row['teacher'])
                    start = datetime.strptime(row['start_time'], '%H:%M').time()
                    end = datetime.strptime(row['end_time'], '%H:%M').time()

                    if Timetable.objects.filter(
                        classroom=classroom, day=row['day'],
                        start_time__lt=end, end_time__gt=start
                    ).exists():
                        errors.append(f"Conflict for {row['classroom']} on {row['day']} at {row['start_time']}")
                        continue

                    Timetable.objects.create(
                        classroom=classroom, teacher=teacher,
                        day=row['day'], start_time=start,
                        end_time=end, subject_name=row.get('subject_name', '')
                    )
                    success_count += 1
                except Exception as e:
                    errors.append(str(e))

            if errors:
                return Response({"message": f"Partial success: {success_count} added", "errors": errors},
                                status=status.HTTP_207_MULTI_STATUS)

            return Response({"message": f"{success_count} entries added successfully"},
                            status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@user_passes_test(is_admin)
def all_timetables(request):
    entries = Timetable.objects.select_related('classroom', 'teacher').all()
    serializer = TimetableSerializer(entries, many=True)
    return Response(serializer.data)

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
        entry = Timetable.objects.get(pk=pk)
        entry.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Timetable.DoesNotExist:
        return Response({'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

