from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from .models import EjemploUso
from Aplicaciones.PalabraInv.models import PalabraInventada

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
