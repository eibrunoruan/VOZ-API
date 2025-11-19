from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from applications.localidades.models import Cidade, Estado
from applications.denuncias.models import Denuncia

class OfficialEntity(models.Model):
    nome = models.CharField(max_length=200)
    
    cidade = models.ForeignKey(Cidade, on_delete=models.PROTECT, related_name='entidades_oficiais', null=True, blank=True)
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT, related_name='entidades_oficiais', null=True, blank=True)
    
    gestores = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        related_name='entidades_gerenciadas',
        limit_choices_to={'tipo_usuario': 'GESTOR_PUBLICO'}
    )

    class Meta:
        verbose_name = _('Entidade Oficial')
        verbose_name_plural = _('Entidades Oficiais')
        constraints = [
            models.UniqueConstraint(fields=['nome', 'cidade', 'estado'], name='entidade_unica_por_localidade')
        ]

    def clean(self):
        if self.cidade and self.estado:
            raise ValidationError(_('A entidade deve ser associada a uma cidade OU a um estado, não a ambos.'))
        if not self.cidade and not self.estado:
            raise ValidationError(_('A entidade deve ser associada a uma cidade ou a um estado.'))

    def __str__(self):
        local = self.cidade if self.cidade else self.estado
        return f'{self.nome} - {local}'

class OfficialResponse(models.Model):
    denuncia = models.OneToOneField(Denuncia, on_delete=models.CASCADE, related_name='resposta_oficial')
    entidade = models.ForeignKey(OfficialEntity, on_delete=models.CASCADE, related_name='respostas')
    texto = models.TextField()
    data_resposta = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Resposta Oficial')
        verbose_name_plural = _('Respostas Oficiais')
        ordering = ['-data_resposta']

    def __str__(self):
        return f'Resposta para "{self.denuncia.titulo}"'