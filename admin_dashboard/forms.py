from django import forms

class UploadFileForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(attrs={'class': 'w-full p-2 border rounded', 'accept': '.csv,.xlsx'}))
