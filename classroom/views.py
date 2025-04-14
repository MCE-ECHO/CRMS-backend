from django.http import HttpResponse

def test_classroom(request):
    return HttpResponse("Classroom app is working!")
