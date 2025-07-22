from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.conf import settings
import requests
import json
from .models import EjemploUso
from Aplicaciones.PalabraInv.models import PalabraInventada
from django.db.models import Count
from django.http import JsonResponse


# Listar ejemplos
def listarEjemplos(request):
    ejemplos = EjemploUso.objects.select_related('palabra', 'autor').all()
    return render(request, "EjemploUsu/inicioEjemplo.html", {'ejemplos': ejemplos})

# Mostrar formulario para nuevo ejemplo
@login_required
def nuevoEjemplo(request):
    palabras = PalabraInventada.objects.all()
    return render(request, "EjemploUsu/nuevoEjemplo.html", {'palabras': palabras})

# Guardar ejemplo
@login_required
def guardarEjemplo(request):
    if request.method == "POST":
        palabra_id = request.POST.get('palabra')
        texto = request.POST.get('texto', '').strip()

        if not palabra_id or not texto:
            messages.warning(request, "Todos los campos son obligatorios.")
            return redirect('nuevoEjemplo')

        palabra = get_object_or_404(PalabraInventada, id=palabra_id)

        EjemploUso.objects.create(
            palabra=palabra,
            texto=texto,
            autor=request.user
        )
        messages.success(request, "Ejemplo registrado correctamente.")
        return redirect('listarEjemplos')

    return redirect('listarEjemplos')

# Editar ejemplo
@login_required
def editarEjemplo(request, id):
    ejemplo = get_object_or_404(EjemploUso, id=id)
    palabras = PalabraInventada.objects.all()
    return render(request, "EjemploUsu/editarEjemplo.html", {'ejemplo': ejemplo, 'palabras': palabras})

# Procesar edición
@login_required
def actualizarEjemplo(request, id):
    ejemplo = get_object_or_404(EjemploUso, id=id)

    if request.method == "POST":
        palabra_id = request.POST.get('palabra')
        texto = request.POST.get('texto', '').strip()

        if not palabra_id or not texto:
            messages.warning(request, "Todos los campos son obligatorios.")
            return redirect('editarEjemplo', id=id)

        palabra = get_object_or_404(PalabraInventada, id=palabra_id)
        ejemplo.palabra = palabra
        ejemplo.texto = texto
        ejemplo.save()

        messages.success(request, "Ejemplo actualizado correctamente.")
        return redirect('listarEjemplos')

    return redirect('listarEjemplos')

# Eliminar ejemplo (requiere permiso)
@permission_required('EjemploUso.delete_ejemplouso', raise_exception=True)
def eliminarEjemplo(request, id):
    ejemplo = get_object_or_404(EjemploUso, id=id)
    ejemplo.delete()
    messages.success(request, "Ejemplo eliminado correctamente.")
    return redirect('listarEjemplos')

def envio_telegram(request, pk):
    ejemplo = get_object_or_404(EjemploUso, pk=pk)
    
    return render(request, 'EjemploUsu/envioEjemplo.html', {
        'ejemplo': ejemplo,
        'tipos_mensaje': ['Consulta', 'Revisión', 'Corrección', 'Otro']
    })

def procesar_mensaje_telegram(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ejemplo = get_object_or_404(EjemploUso, pk=data.get('ejemplo_id'))
            
            chat_id = ejemplo.telegram_chat_id
            
            if not chat_id:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Este ejemplo no tiene un chat de Telegram vinculado. Pídale al autor que inicie chat con el bot.'
                }, status=400)
            
            # Construir mensaje
            tipo_mensaje = data.get('tipo_mensaje')
            contenido = data.get('contenido', '')
            mensaje_adicional = data.get('mensaje_adicional', '')

            mensaje = (
                f"📝 *{tipo_mensaje.upper()} SOBRE EJEMPLO DE USO*\n\n"
                f"🔹 *Palabra:* {ejemplo.palabra.palabra}\n"
                f"🔹 *Ejemplo actual:* {ejemplo.texto}\n"
                f"🔹 *Contenido nuevo:* {contenido}\n"
            )

            if mensaje_adicional:
                mensaje += f"\n📌 *Comentarios adicionales:*\n{mensaje_adicional}\n"

            mensaje += f"\nEnviado por: {request.user.username}"
            
            # Enviar mensaje vía Telegram API
            bot_token = settings.TELEGRAM_BOT_TOKEN
            send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            
            response = requests.post(send_url, json={
                'chat_id': chat_id,
                'text': mensaje,
                'parse_mode': 'Markdown'
            })
            
            if response.status_code != 200:
                error_data = response.json()
                error_msg = error_data.get('description', 'Error desconocido de Telegram')
                return JsonResponse({
                    'status': 'error',
                    'message': f'Error al enviar: {error_msg}. Verifica que el bot tenga permisos.'
                }, status=400)
                
            return JsonResponse({
                'status': 'success',
                'message': 'Mensaje enviado correctamente al autor por Telegram.'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Solicitud JSON inválida.'}, status=400)
        except EjemploUso.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Ejemplo no encontrado.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Error interno: {str(e)}'}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

def ayuda_telegram(request):
    """Muestra instrucciones para vincular Telegram"""
    return render(request, 'EjemploUsu/ayuda_telegram.html')

def graficos_ejemplos(request):
    """Vista para mostrar la página de gráficos"""
    return render(request, 'EjemploUsu/graficos.html')

def datos_graficos_ejemplos(request):
    """API que devuelve datos para el gráfico de palabras más usadas"""
    try:
        # Palabras más usadas en ejemplos (top 5)
        palabras_data = EjemploUso.objects.values('palabra__palabra') \
            .annotate(total=Count('id')) \
            .order_by('-total')[:5]
        
        data = {
            'labels': [p['palabra__palabra'] for p in palabras_data],
            'data': [p['total'] for p in palabras_data],
            'colors': ['#3498db', '#2ecc71', '#e74c3c', '#f1c40f', '#9b59b6']
        }
        
        return JsonResponse(data)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)