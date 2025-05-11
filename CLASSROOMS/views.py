from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

@csrf_exempt
@require_POST
def toggle_dark_mode(request):
    data = json.loads(request.body)
    dark_mode = data.get('dark_mode', False)
    request.session['dark_mode'] = dark_mode
    return JsonResponse({'status': 'success'})
