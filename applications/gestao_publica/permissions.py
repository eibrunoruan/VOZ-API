from rest_framework import permissions
from applications.denuncias.models import Denuncia

class IsGestorWithJurisdiction(permissions.BasePermission):
    message = "Você não tem permissão para executar esta ação nesta denúncia."

    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, Denuncia):
            return False

        user = request.user

        if not hasattr(user, 'tipo_usuario') or user.tipo_usuario != 'GESTOR_PUBLICO':
            return False

        entidade_gerenciada = user.entidades_gerenciadas.first()
        if not entidade_gerenciada:
            return False

        if entidade_gerenciada.cidade:
            return obj.cidade == entidade_gerenciada.cidade and obj.jurisdicao == Denuncia.Jurisdicao.MUNICIPAL
        
        if entidade_gerenciada.estado:
            return obj.estado == entidade_gerenciada.estado and obj.jurisdicao == Denuncia.Jurisdicao.ESTADUAL

        return False
