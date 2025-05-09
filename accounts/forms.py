from django import forms
from .models import TeacherProfile, StudentProfile, Event

class ProfileForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = ['department', 'avatar', 'phone']
        widgets = {
            'department': forms.TextInput(attrs={'class': 'w-full p-3 border rounded-lg'}),
            'phone': forms.TextInput(attrs={'class': 'w-full p-3 border rounded-lg'}),
        }

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['roll_number', 'avatar', 'phone']
        widgets = {
            'roll_number': forms.TextInput(attrs={'class': 'w-full p-3 border rounded-lg'}),
            'phone': forms.TextInput(attrs={'class': 'w-full p-3 border rounded-lg'}),
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

