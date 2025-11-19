from django.db import models

class Estado(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    uf = models.CharField(max_length=2, unique=True)

    class Meta:
        verbose_name = 'Estado'
        verbose_name_plural = 'Estados'

    def __str__(self):
        return self.nome

class Cidade(models.Model):
    nome = models.CharField(max_length=100)
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT, related_name='cidades')

    class Meta:
        verbose_name = 'Cidade'
        verbose_name_plural = 'Cidades'
        unique_together = [['nome', 'estado']]

    def __str__(self):
        return f'{self.nome}, {self.estado.uf}'