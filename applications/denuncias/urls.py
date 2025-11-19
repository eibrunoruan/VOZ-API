from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoriaViewSet, DenunciaViewSet, ApoioDenunciaViewSet, ComentarioViewSet

router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'denuncias', DenunciaViewSet, basename='denuncia')
router.register(r'apoios', ApoioDenunciaViewSet, basename='apoio')
router.register(r'comentarios', ComentarioViewSet, basename='comentario')

urlpatterns = [
    path('', include(router.urls)),
]