from django import forms
from accounts.models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'start_date', 'end_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full p-3 border rounded-lg'}),
            'description': forms.Textarea(attrs={'class': 'w-full p-3 border rounded-lg', 'rows': 4}),
            'start_date': forms.DateTimeInput(attrs={'class': 'w-full p-3 border rounded-lg', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'w-full p-3 border rounded-lg', 'type': 'datetime-local'}),
        }

