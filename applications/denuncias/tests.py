from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from applications.core.models import User
from .models import Denuncia, Categoria, Comentario
from applications.localidades.models import Estado, Cidade
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image

def create_dummy_image():
    """
    Cria uma imagem PNG 1x1 em memória para testes.
    """
    image_file = BytesIO()
    image = Image.new('RGB', (1, 1), 'black')
    image.save(image_file, 'png')
    image_file.seek(0)
    return SimpleUploadedFile('test.png', image_file.read(), content_type='image/png')


class DenunciaAPITests(APITestCase):
    def setUp(self):
        self.estado = Estado.objects.create(nome='Test Estado', uf='TE')
        self.cidade = Cidade.objects.create(nome='Test Cidade', estado=self.estado)
        self.categoria = Categoria.objects.create(nome='Test Categoria')
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123', first_name='Test')
        self.client.login(username='testuser', password='password123')

    def test_create_denuncia_as_guest(self):
        self.client.logout()
        url = reverse('denuncia-list')
        image = create_dummy_image()
        data = {
            'titulo': 'Denúncia de Teste Convidado',
            'descricao': 'Descrição da denúncia de teste.',
            'autor_convidado': 'Convidado Anônimo',
            'categoria': self.categoria.id,
            'cidade': self.cidade.id,
            'estado': self.estado.id,
            'latitude': -23.550520,
            'longitude': -46.633308,
            'jurisdicao': 'MUNICIPAL',
            'foto': image,
        }
        response = self.client.post(url, data, format='multipart')
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
        self.assertEqual(Denuncia.objects.count(), 1)
        denuncia = Denuncia.objects.get()
        self.assertEqual(denuncia.autor_convidado, 'Convidado Anônimo')
        self.assertIsNone(denuncia.autor)

    def test_create_denuncia_as_authenticated_user(self):
        url = reverse('denuncia-list')
        image = create_dummy_image()
        data = {
            'titulo': 'Denúncia de Teste Autenticado',
            'descricao': 'Descrição da denúncia de teste.',
            'categoria': self.categoria.id,
            'cidade': self.cidade.id,
            'estado': self.estado.id,
            'latitude': -23.550520,
            'longitude': -46.633308,
            'jurisdicao': 'MUNICIPAL',
            'foto': image,
        }
        response = self.client.post(url, data, format='multipart')
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
        self.assertEqual(Denuncia.objects.count(), 1)
        denuncia = Denuncia.objects.get()
        self.assertEqual(denuncia.autor, self.user)
        self.assertIsNone(denuncia.autor_convidado)

class ComentarioAPITests(APITestCase):
    def setUp(self):
        self.estado = Estado.objects.create(nome='Test Estado', uf='TE')
        self.cidade = Cidade.objects.create(nome='Test Cidade', estado=self.estado)
        self.categoria = Categoria.objects.create(nome='Test Categoria')
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123', first_name='Test')
        self.denuncia = Denuncia.objects.create(
            titulo='Denúncia de Teste',
            descricao='Descrição da denúncia de teste.',
            autor=self.user,
            categoria=self.categoria,
            cidade=self.cidade,
            estado=self.estado,
            latitude=-23.550520,
            longitude=-46.633308,
            jurisdicao='MUNICIPAL',
            foto=create_dummy_image()
        )
        self.client.login(username='testuser', password='password123')

    def test_create_comentario_as_guest(self):
        self.client.logout()
        url = reverse('comentario-list')
        data = {
            'denuncia': self.denuncia.id,
            'texto': 'Comentário de um convidado.',
            'autor_convidado': 'Convidado Comentarista',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comentario.objects.count(), 1)
        comentario = Comentario.objects.get()
        self.assertEqual(comentario.autor_convidado, 'Convidado Comentarista')
        self.assertIsNone(comentario.autor)

    def test_create_comentario_as_authenticated_user(self):
        url = reverse('comentario-list')
        data = {
            'denuncia': self.denuncia.id,
            'texto': 'Comentário de um usuário autenticado.',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comentario.objects.count(), 1)
        comentario = Comentario.objects.get()
        self.assertEqual(comentario.autor, self.user)
        self.assertIsNone(comentario.autor_convidado)