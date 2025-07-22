from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Permission
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from Aplicaciones.PalabraInv.models import PalabraInventada
import os
from django.contrib.contenttypes.models import ContentType


class PalabraInventadaViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Configuración inicial para todas las pruebas
        cls.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        cls.admin_user = User.objects.create_superuser(
            username='admin',
            password='adminpass123',
            email='admin@example.com'
        )
        
        # Crear permiso de eliminación
        content_type = ContentType.objects.get_for_model(PalabraInventada)
        permission = Permission.objects.get(
            codename='delete_palabrainventada',
            content_type=content_type,
        )
        cls.admin_user.user_permissions.add(permission)
        
        # Crear palabra de prueba
        cls.palabra = PalabraInventada.objects.create(
            creador=cls.user,
            palabra='Testpalabra',
            significado='Significado de prueba'
        )

    def setUp(self):
        self.client = Client()
        
    def test_listarPalabras(self):
        response = self.client.get(reverse('listarPalabras'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'PalabraInv/inicioPalabra.html')
        self.assertContains(response, 'Testpalabra')
        print("✅ test_listarPalabras pasó correctamente.")

    def test_nuevaPalabra_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('nuevaPalabra'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'PalabraInv/nuevaPalabra.html')
        print("✅ test_nuevaPalabra_authenticated pasó correctamente.")

    def test_nuevaPalabra_unauthenticated(self):
        response = self.client.get(reverse('nuevaPalabra'))
        self.assertEqual(response.status_code, 302)  # Redirige a login
        print("✅ test_nuevaPalabra_unauthenticated pasó correctamente.")

    def test_guardarPalabra_valid(self):
        self.client.login(username='testuser', password='testpass123')
        
        # Crear una imagen de prueba
        test_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'simple image content',
            content_type='image/jpeg'
        )
        
        data = {
            'palabra': 'NuevaPalabra',
            'significado': 'Nuevo significado',
            'imagen': test_image
        }
        
        response = self.client.post(reverse('guardarPalabra'), data)
        self.assertEqual(response.status_code, 302)  # Redirección después de éxito
        self.assertTrue(PalabraInventada.objects.filter(palabra='NuevaPalabra').exists())
        
        # Verificar mensaje de éxito
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Palabra registrada exitosamente.")
        print("✅ test_guardarPalabra_valid pasó correctamente.")

    def test_guardarPalabra_invalid(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'palabra': '',
            'significado': ''
        }
        response = self.client.post(reverse('guardarPalabra'), data)
        self.assertEqual(response.status_code, 302)  # Redirección por error
        
        # Verificar mensaje de error
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Los campos palabra y significado son obligatorios.")
        print("✅ test_guardarPalabra_invalid pasó correctamente.")

    def test_guardarPalabra_duplicate(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'palabra': 'Testpalabra',  # Palabra ya existe
            'significado': 'Otro significado'
        }
        response = self.client.post(reverse('guardarPalabra'), data)
        self.assertEqual(response.status_code, 302)  # Redirección por error
        
        # Verificar mensaje de error
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Ya existe una palabra con ese nombre.")
        print("✅ test_guardarPalabra_duplicate pasó correctamente.")

    def test_editarPalabra(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('editarPalabra', args=[self.palabra.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'PalabraInv/editarPalabra.html')
        self.assertContains(response, 'Testpalabra')
        print("✅ test_editarPalabra pasó correctamente.")

    def test_actualizarPalabra(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'palabra': 'PalabraActualizada',
            'significado': 'Significado actualizado'
        }
        response = self.client.post(reverse('actualizarPalabra', args=[self.palabra.id]), data)
        self.assertEqual(response.status_code, 302)  # Redirección después de éxito
        
        # Verificar actualización
        self.palabra.refresh_from_db()
        self.assertEqual(self.palabra.palabra, 'PalabraActualizada')
        
        # Verificar mensaje de éxito
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Palabra actualizada correctamente.")
        print("✅ test_actualizarPalabra pasó correctamente.")

    def test_eliminarPalabra_admin(self):
        self.client.login(username='admin', password='adminpass123')
        palabra_id = self.palabra.id
        response = self.client.get(reverse('eliminarPalabra', args=[palabra_id]))
        self.assertEqual(response.status_code, 302)  # Redirección después de éxito
        self.assertFalse(PalabraInventada.objects.filter(id=palabra_id).exists())
        
        # Verificar mensaje de éxito
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Palabra eliminada correctamente.")
        print("✅ test_eliminarPalabra_admin pasó correctamente.")

    def test_eliminarPalabra_non_admin(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('eliminarPalabra', args=[self.palabra.id]))
        self.assertEqual(response.status_code, 403)  # Prohibido
        print("✅ test_eliminarPalabra_non_admin pasó correctamente.")

    def test_calendarioPalabras(self):
        response = self.client.get(reverse('calendarioPalabras'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'PalabraInv/calendario.html')
        print("✅ test_calendarioPalabras pasó correctamente.")

    def test_eventosPalabras(self):
        response = self.client.get(reverse('eventosPalabras'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        
        # Verificar contenido del JSON
        data = response.json()
        self.assertTrue(isinstance(data, list))
        self.assertIn('title', data[0])
        print("✅ test_eventosPalabras pasó correctamente.")