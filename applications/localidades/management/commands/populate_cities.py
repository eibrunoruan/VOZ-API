import requests
from django.core.management.base import BaseCommand
from applications.localidades.models import Estado, Cidade

class Command(BaseCommand):
    help = 'Popula o banco de dados com as cidades do Brasil a partir da API do IBGE.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando a população de cidades...'))

        estados = Estado.objects.all()
        if not estados.exists():
            self.stdout.write(self.style.ERROR('Nenhum estado encontrado no banco de dados. Execute a migração para popular os estados primeiro.'))
            return

        for estado in estados:
            self.stdout.write(f'Buscando cidades para o estado de {estado.nome}...')
            try:
                response = requests.get(f'https://servicodados.ibge.gov.br/api/v1/localidades/estados/{estado.uf}/municipios')
                response.raise_for_status()
                cidades_data = response.json()

                for cidade_data in cidades_data:
                    nome_cidade = cidade_data['nome']
                    if not Cidade.objects.filter(nome=nome_cidade, estado=estado).exists():
                        Cidade.objects.create(nome=nome_cidade, estado=estado)
                        self.stdout.write(self.style.SUCCESS(f'  - Cidade "{nome_cidade}" adicionada.'))
                    else:
                        self.stdout.write(self.style.WARNING(f'  - Cidade "{nome_cidade}" já existe.'))

            except requests.exceptions.RequestException as e:
                self.stdout.write(self.style.ERROR(f'Erro ao buscar cidades para {estado.nome}: {e}'))

        self.stdout.write(self.style.SUCCESS('População de cidades concluída!'))
