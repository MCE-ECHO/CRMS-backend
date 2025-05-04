from django import forms

class UploadFileForm(forms.Form):
    file = forms.FileField(
        label='Select a CSV or Excel file',
        widget=forms.FileInput(attrs={'accept': '.csv,.xlsx', 'class': 'w-full p-3 border rounded-lg', 'id': 'fileInput'})
    )
