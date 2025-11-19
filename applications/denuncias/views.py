from rest_framework import viewsets, permissions, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from applications.gestao_publica.permissions import IsGestorWithJurisdiction
from .models import Categoria, Denuncia, ApoioDenuncia, Comentario
from .serializers import CategoriaSerializer, DenunciaSerializer, ApoioDenunciaSerializer, ComentarioSerializer
from .services import criar_ou_apoiar_denuncia

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if not request.user.is_authenticated:
            return False

        if hasattr(obj, 'autor') and obj.autor is not None:
            return obj.autor == request.user
        if hasattr(obj, 'apoiador') and obj.apoiador is not None:
            return obj.apoiador == request.user
        
        return False

class CategoriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.AllowAny]

class DenunciaViewSet(viewsets.ModelViewSet):
    queryset = Denuncia.objects.all().select_related(
        'autor', 'categoria', 'cidade', 'estado'
    ).prefetch_related('apoios', 'comentarios')
    serializer_class = DenunciaSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        
        status_param = self.request.query_params.get('status', None)
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        categoria_param = self.request.query_params.get('categoria', None)
        if categoria_param:
            queryset = queryset.filter(categoria_id=categoria_param)
        
        return queryset

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user if request.user.is_authenticated else None
        autor_convidado = serializer.validated_data.get('autor_convidado')

        if not user and not autor_convidado:
            return Response(
                {'detail': 'É necessário fornecer um nome de convidado.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        denuncia, created_denuncia, created_apoio = criar_ou_apoiar_denuncia(
            serializer.validated_data,
            user=user,
            autor_convidado=autor_convidado
        )

        response_serializer = self.get_serializer(denuncia)
        headers = self.get_success_headers(response_serializer.data)

        if created_denuncia:
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        
        elif created_apoio:
            return Response(
                {
                    'message': 'Denúncia similar encontrada próxima. Seu apoio foi registrado!',
                    'apoio_adicionado': True,
                    'denuncia': response_serializer.data
                },
                status=status.HTTP_200_OK,
                headers=headers
            )
        
        else:
            return Response(
                {
                    'message': 'Você já apoiou esta denúncia anteriormente.',
                    'apoio_adicionado': False,
                    'denuncia': response_serializer.data
                },
                status=status.HTTP_200_OK,
                headers=headers
            )

    def destroy(self, request, *args, **kwargs):
        from .services import haversine_distance, SEARCH_RADIUS_METERS
        from django.db import transaction
        
        denuncia = self.get_object()
        
        if request.user.is_authenticated:
            if denuncia.autor != request.user:
                return Response(
                    {'detail': 'Apenas o autor pode deletar sua própria denúncia.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        apoios = list(denuncia.apoios.all().select_related('apoiador'))
        total_apoios = len(apoios)
        
        if total_apoios > 0:
            with transaction.atomic():
                denuncias_proximas = Denuncia.objects.filter(
                    categoria=denuncia.categoria,
                    status__in=['ABERTA', 'EM_ANALISE']
                ).exclude(id=denuncia.id)
                
                denuncia_destino = None
                for candidata in denuncias_proximas:
                    distancia = haversine_distance(
                        denuncia.latitude, denuncia.longitude,
                        candidata.latitude, candidata.longitude
                    )
                    if distancia <= SEARCH_RADIUS_METERS:
                        denuncia_destino = candidata
                        break
                
                if denuncia_destino:
                    apoios_transferidos = 0
                    for apoio in apoios:
                        if not denuncia_destino.apoios.filter(apoiador=apoio.apoiador).exists():
                            apoio.denuncia = denuncia_destino
                            apoio.save()
                            apoios_transferidos += 1
                        else:
                            apoio.delete()
                    
                    denuncia.delete()
                    
                    return Response(
                        {
                            'message': f'Denúncia deletada com sucesso. {apoios_transferidos} apoio(s) foram transferidos para uma denúncia similar próxima.',
                            'apoios_transferidos': apoios_transferidos,
                            'denuncia_destino_id': denuncia_destino.id
                        },
                        status=status.HTTP_200_OK
                    )
                else:
                    apoio_mais_antigo = apoios[0] if apoios else None
                    
                    if apoio_mais_antigo:
                        nova_denuncia = Denuncia.objects.create(
                            titulo=denuncia.titulo,
                            descricao=f"[Denúncia promovida automaticamente] {denuncia.descricao}",
                            autor=apoio_mais_antigo.apoiador,
                            categoria=denuncia.categoria,
                            cidade=denuncia.cidade,
                            estado=denuncia.estado,
                            foto=denuncia.foto,
                            endereco=denuncia.endereco,
                            latitude=denuncia.latitude,
                            longitude=denuncia.longitude,
                            jurisdicao=denuncia.jurisdicao,
                            status=denuncia.status
                        )
                        
                        for apoio in apoios[1:]:
                            if not nova_denuncia.apoios.filter(apoiador=apoio.apoiador).exists():
                                apoio.denuncia = nova_denuncia
                                apoio.save()
                        
                        apoio_mais_antigo.delete()
                        
                        denuncia.delete()
                        
                        return Response(
                            {
                                'message': f'Denúncia deletada com sucesso. O apoio mais antigo foi promovido como nova denúncia principal e {len(apoios)-1} apoio(s) foram preservados.',
                                'nova_denuncia_id': nova_denuncia.id,
                                'apoios_preservados': len(apoios) - 1
                            },
                            status=status.HTTP_200_OK
                        )
        
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def resolver(self, request, pk=None):
        denuncia = self.get_object()
        if denuncia.autor != request.user:
            return Response(
                {'detail': 'Apenas o autor pode marcar a denúncia como resolvida.'},
                status=status.HTTP_403_FORBIDDEN
            )
        denuncia.status = Denuncia.Status.RESOLVIDA
        denuncia.save()
        serializer = self.get_serializer(denuncia)
        return Response(serializer.data)

    @action(
        detail=True, 
        methods=['post'], 
        permission_classes=[permissions.IsAuthenticated, IsGestorWithJurisdiction]
    )
    def change_status(self, request, pk=None):
        denuncia = self.get_object()
        novo_status = request.data.get('status')
        if not novo_status:
            return Response(
                {'error': 'O campo "status" é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        status_choices = [choice[0] for choice in Denuncia.Status.choices]
        if novo_status not in status_choices:
            return Response(
                {'error': f'Status inválido. Opções válidas: {status_choices}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        denuncia.status = novo_status
        denuncia.save()
        serializer = self.get_serializer(denuncia)
        return Response(serializer.data)

class ApoioDenunciaViewSet(mixins.CreateModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.DestroyModelMixin,
                           mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    serializer_class = ApoioDenunciaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ApoioDenuncia.objects.filter(apoiador=self.request.user)

    def perform_create(self, serializer):
        serializer.save(apoiador=self.request.user)

class ComentarioViewSet(viewsets.ModelViewSet):
    serializer_class = ComentarioSerializer
    
    def get_permissions(self):
        if self.action == 'destroy':
            permission_classes = [IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = Comentario.objects.select_related('autor').all()
        denuncia_id = self.request.query_params.get('denuncia_id')
        if denuncia_id is not None:
            queryset = queryset.filter(denuncia_id=denuncia_id)
        return queryset

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        autor_convidado = serializer.validated_data.get('autor_convidado')

        if not user and not autor_convidado:
            raise ValidationError('É necessário estar autenticado ou fornecer um nome de convidado.')

        serializer.save(autor=user, autor_convidado=autor_convidado)