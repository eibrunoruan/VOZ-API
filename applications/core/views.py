from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from applications.denuncias.models import Denuncia, Categoria
from applications.localidades.models import Estado, Cidade
from applications.core.models import User
from django.conf import settings
import time
import cloudinary

@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    # Verificar se Cloudinary está configurado
    cloudinary_config = cloudinary.config()
    cloudinary_status = {
        "configured": bool(cloudinary_config.cloud_name),
        "cloud_name": cloudinary_config.cloud_name or "NOT_CONFIGURED",
        "storage_backend": settings.DEFAULT_FILE_STORAGE
    }
    
    return JsonResponse({
        "status": "ok",
        "message": "API is running",
        "timestamp": time.time(),
        "cloudinary": cloudinary_status
    })

@csrf_exempt
@require_http_methods(["GET"])
def performance_test(request):
    try:
        stats = {
            "total_denuncias": Denuncia.objects.count(),
            "total_categorias": Categoria.objects.count(),
            "total_estados": Estado.objects.count(),
            "total_cidades": Cidade.objects.count(),
            "total_usuarios": User.objects.count(),
            "timestamp": time.time(),
            "status": "ok"
        }
        return JsonResponse(stats)
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e),
            "timestamp": time.time()
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def echo_test(request):
    return JsonResponse({
        "echo": "pong",
        "timestamp": time.time()
    })
