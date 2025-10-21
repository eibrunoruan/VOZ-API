from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from applications.localidades.models import Cidade, Estado

class Categoria(models.Model):
    """Modelo para as categorias de denúncias (ex: Iluminação, Saneamento)."""
    nome = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = _('Categoria')
        verbose_name_plural = _('Categorias')

    def __str__(self):
        return self.nome

class Denuncia(models.Model):
    """A entidade central do sistema, representando uma denúncia."""

    class Jurisdicao(models.TextChoices):
        MUNICIPAL = 'MUNICIPAL', _('Municipal')
        ESTADUAL = 'ESTADUAL', _('Estadual')
        FEDERAL = 'FEDERAL', _('Federal')
        PRIVADO = 'PRIVADO', _('Privado')

    class Status(models.TextChoices):
        ABERTA = 'ABERTA', _('Aberta')
        EM_ANALISE = 'EM_ANALISE', _('Em Análise')
        RESOLVIDA = 'RESOLVIDA', _('Resolvida')

    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='denuncias'
    )
    autor_convidado = models.CharField(max_length=150, null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='denuncias')
    cidade = models.ForeignKey(Cidade, on_delete=models.PROTECT, related_name='denuncias')
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT, related_name='denuncias')
    
    # A foto é obrigatória
    foto = models.ImageField(upload_to='denuncias_fotos/', blank=False, null=False)
    
    # Usar DecimalField para precisão de coordenadas
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    
    jurisdicao = models.CharField(max_length=20, choices=Jurisdicao.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ABERTA)
    
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Denúncia')
        verbose_name_plural = _('Denúncias')
        ordering = ['-data_criacao']

    def __str__(self):
        return self.titulo

class ApoioDenuncia(models.Model):
    """Representa o apoio (reclamação agrupada) de um usuário a uma denúncia existente."""
    denuncia = models.ForeignKey(Denuncia, on_delete=models.CASCADE, related_name='apoios')
    apoiador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='apoios_dados')
    data_apoio = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Apoio de Denúncia')
        verbose_name_plural = _('Apoios de Denúncias')
        # Garante que um usuário só pode apoiar uma denúncia uma única vez
        unique_together = [['denuncia', 'apoiador']]

    def __str__(self):
        return f'{self.apoiador} apoiou {self.denuncia.titulo}'

class Comentario(models.Model):
    """
    Representa um comentário feito por um usuário em uma denúncia.
    """
    denuncia = models.ForeignKey(Denuncia, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='comentarios_feitos'
    )
    autor_convidado = models.CharField(max_length=150, null=True, blank=True)
    texto = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Comentário')
        verbose_name_plural = _('Comentários')
        ordering = ['data_criacao']

    def __str__(self):
        return f'Comentário de {self.autor} em "{self.denuncia.titulo}"'