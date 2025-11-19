from django.contrib import admin
from .models import Categoria, Denuncia, ApoioDenuncia

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

@admin.register(Denuncia)
class DenunciaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'categoria', 'cidade', 'status', 'data_criacao')
    list_filter = ('status', 'jurisdicao', 'categoria', 'estado', 'cidade')
    search_fields = ('titulo', 'descricao', 'autor__email')
    readonly_fields = ('data_criacao',)
    list_select_related = ('autor', 'categoria', 'cidade', 'estado')
    
    fieldsets = (
        ('Informações Gerais', {
            'fields': ('titulo', 'descricao', 'autor', 'foto')
        }),
        ('Localização e Categoria', {
            'fields': ('categoria', 'latitude', 'longitude', 'cidade', 'estado')
        }),
        ('Status e Jurisdição', {
            'fields': ('status', 'jurisdicao', 'data_criacao')
        }),
    )

@admin.register(ApoioDenuncia)
class ApoioDenunciaAdmin(admin.ModelAdmin):
    list_display = ('denuncia', 'apoiador', 'data_apoio')
    search_fields = ('denuncia__titulo', 'apoiador__email')
    list_select_related = ('denuncia', 'apoiador')