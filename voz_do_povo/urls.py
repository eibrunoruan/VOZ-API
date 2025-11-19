from django.contrib import admin
from django.urls import path, include
from applications.core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health/', core_views.health_check, name='health_check'),
    path('api/performance/', core_views.performance_test, name='performance_test'),
    path('api/echo/', core_views.echo_test, name='echo_test'),
    path('api/auth/', include('applications.autenticacao.urls')),
    path('api/denuncias/', include('applications.denuncias.urls')),
    path('api/localidades/', include('applications.localidades.urls')),
    path('api/gestao/', include('applications.gestao_publica.urls')),
]
