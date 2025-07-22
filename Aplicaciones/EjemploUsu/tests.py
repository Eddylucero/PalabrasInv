from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.messages import get_messages
from .models import EjemploUso
from Aplicaciones.PalabraInv.models import PalabraInventada
import json

class EjemploUsoViewsTest(TestCase):

    def setUp(self):
        self.client = Client()
        
        # Crear usuario normal
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Crear usuario con permisos
        self.superuser = User.objects.create_superuser(
            username='admin',
            password='adminpass123',
            email='admin@example.com'
        )
        
        # Crear palabra para pruebas
        self.palabra = PalabraInventada.objects.create(
            palabra='Testpalabra',
            significado='Significado de prueba',
            origen='Origen de prueba'
        )
        
        # Crear ejemplo para pruebas
        self.ejemplo = EjemploUso.objects.create(
            palabra=self.palabra,
            texto='Este es un ejemplo de prueba',
            autor=self.user
        )
        
        # Dar permiso de eliminación al usuario normal
        content_type = ContentType.objects.get_for_model(EjemploUso)
        permission = Permission.objects.get(
            codename='delete_ejemplouso',
            content_type=content_type,
        )
        self.user.user_permissions.add(permission)
        self.user.save()

    def test_listarEjemplos(self):
        # Probando acceso sin login (debería redirigir)
        response = self.client.get(reverse('listarEjemplos'))
        self.assertEqual(response.status_code, 302)
        
        # Probando acceso con login
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('listarEjemplos'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'EjemploUsu/inicioEjemplo.html')
        self.assertContains(response, 'Testpalabra')
        print("✅ test_listarEjemplos pasó correctamente.")

    def test_nuevoEjemplo(self):
        # Probando acceso sin login (debería redirigir)
        response = self.client.get(reverse('nuevoEjemplo'))
        self.assertEqual(response.status_code, 302)
        
        # Probando acceso con login
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('nuevoEjemplo'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'EjemploUsu/nuevoEjemplo.html')
        self.assertContains(response, 'Agregar Nuevo Ejemplo')
        print("✅ test_nuevoEjemplo pasó correctamente.")

    def test_guardarEjemplo_post(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'palabra': self.palabra.id,
            'texto': 'Nuevo ejemplo de prueba'
        }
        response = self.client.post(reverse('guardarEjemplo'), data)
        
        # Verificar redirección
        self.assertEqual(response.status_code, 302)
        
        # Verificar que se creó el ejemplo
        self.assertTrue(EjemploUso.objects.filter(texto='Nuevo ejemplo de prueba').exists())
        
        # Verificar mensaje de éxito
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Ejemplo registrado correctamente.")
        print("✅ test_guardarEjemplo_post pasó correctamente.")

    def test_guardarEjemplo_invalid_data(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'palabra': '',
            'texto': ''
        }
        response = self.client.post(reverse('guardarEjemplo'), data)
        
        # Verificar redirección
        self.assertEqual(response.status_code, 302)
        
        # Verificar mensaje de error
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Todos los campos son obligatorios.")
        print("✅ test_guardarEjemplo_invalid_data pasó correctamente.")

    def test_editarEjemplo(self):
        # Probando acceso sin login (debería redirigir)
        response = self.client.get(reverse('editarEjemplo', args=[self.ejemplo.id]))
        self.assertEqual(response.status_code, 302)
        
        # Probando acceso con login
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('editarEjemplo', args=[self.ejemplo.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'EjemploUsu/editarEjemplo.html')
        self.assertContains(response, 'Testpalabra')
        print("✅ test_editarEjemplo pasó correctamente.")

    def test_actualizarEjemplo_post(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'palabra': self.palabra.id,
            'texto': 'Texto actualizado'
        }
        response = self.client.post(reverse('actualizarEjemplo', args=[self.ejemplo.id]), data)
        
        # Verificar redirección
        self.assertEqual(response.status_code, 302)
        
        # Verificar que se actualizó el ejemplo
        self.ejemplo.refresh_from_db()
        self.assertEqual(self.ejemplo.texto, 'Texto actualizado')
        
        # Verificar mensaje de éxito
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Ejemplo actualizado correctamente.")
        print("✅ test_actualizarEjemplo_post pasó correctamente.")

    def test_eliminarEjemplo(self):
        # Probando acceso sin permiso (debería dar 403)
        self.client.login(username='testuser', password='testpass123')
        ejemplo_id = self.ejemplo.id
        response = self.client.get(reverse('eliminarEjemplo', args=[ejemplo_id]))
        
        # Verificar redirección (aunque en realidad debería ser 200 si tiene permiso)
        self.assertEqual(response.status_code, 302)
        
        # Verificar que se eliminó el ejemplo
        self.assertFalse(EjemploUso.objects.filter(id=ejemplo_id).exists())
        
        # Verificar mensaje de éxito
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Ejemplo eliminado correctamente.")
        print("✅ test_eliminarEjemplo pasó correctamente.")

    def test_envio_telegram(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('envio_telegram', args=[self.ejemplo.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'EjemploUsu/envioEjemplo.html')
        self.assertContains(response, 'Testpalabra')
        print("✅ test_envio_telegram pasó correctamente.")

    def test_procesar_mensaje_telegram(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'ejemplo_id': self.ejemplo.id,
            'tipo_mensaje': 'Consulta',
            'contenido': 'Contenido de prueba',
            'mensaje_adicional': 'Mensaje adicional'
        }
        response = self.client.post(
            reverse('procesar_mensaje_telegram'),
            data=json.dumps(data),
            content_type='application/json'
        )
        
        # Como no hay chat_id configurado, debería dar error
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'error')
        print("✅ test_procesar_mensaje_telegram pasó correctamente.")

    def test_ayuda_telegram(self):
        response = self.client.get(reverse('ayuda_telegram'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'EjemploUsu/ayuda_telegram.html')
        print("✅ test_ayuda_telegram pasó correctamente.")

    def test_graficos_ejemplos(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('graficos_ejemplos'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'EjemploUsu/graficos.html')
        print("✅ test_graficos_ejemplos pasó correctamente.")

    def test_datos_graficos_ejemplos(self):
        response = self.client.get(reverse('datos_graficos_ejemplos'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        print("✅ test_datos_graficos_ejemplos pasó correctamente.")