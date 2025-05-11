from django import forms
from .models import TeacherProfile, StudentProfile, Event
from booking.models import Booking
from classroom.models import Classroom

class ProfileForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = ['avatar', 'role']
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'w-full p-3 border rounded-lg'}),
            'role': forms.Select(attrs={'class': 'w-full p-3 border rounded-lg'}),
        }

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['avatar', 'role']
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'w-full p-3 border rounded-lg'}),
            'role': forms.Select(attrs={'class': 'w-full p-3 border rounded-lg'}),
        }

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'start_date', 'end_date', 'visibility']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full p-3 border rounded-lg'}),
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'w-full p-3 border rounded-lg'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'w-full p-3 border rounded-lg'}),
            'visibility': forms.Select(attrs={'class': 'w-full p-3 border rounded-lg'}),
        }

class BookingForm(forms.ModelForm):
    classroom = forms.ModelChoiceField(
        queryset=Classroom.objects.all(),
        widget=forms.Select(attrs={'class': 'w-full p-3 border rounded-lg'})
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full p-3 border rounded-lg'})
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'w-full p-3 border rounded-lg'})
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'w-full p-3 border rounded-lg'})
    )

    class Meta:
        model = Booking
        fields = ['classroom', 'date', 'start_time', 'end_time']
