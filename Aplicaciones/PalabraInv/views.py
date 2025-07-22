from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import PalabraInventada
from django.contrib.auth.decorators import permission_required, login_required
from django.http import JsonResponse

# Listar palabras
def listarPalabras(request):
    palabras = PalabraInventada.objects.all()
    return render(request, "PalabraInv/inicioPalabra.html", {'palabras': palabras})

# Mostrar formulario para nueva palabra
@login_required
def nuevaPalabra(request):
    return render(request, "PalabraInv/nuevaPalabra.html")

# Guardar palabra
@login_required
def guardarPalabra(request):
    if request.method == "POST":
        palabra = request.POST.get('palabra', '').strip()
        significado = request.POST.get('significado', '').strip()
        imagen = request.FILES.get('imagen', None)

        if not palabra or not significado:
            messages.warning(request, "Los campos palabra y significado son obligatorios.")
            return redirect('nuevaPalabra')

        if PalabraInventada.objects.filter(palabra=palabra).exists():
            messages.error(request, "Ya existe una palabra con ese nombre.")
            return redirect('nuevaPalabra')

        PalabraInventada.objects.create(
            creador=request.user,
            palabra=palabra,
            significado=significado,
            imagen=imagen
        )
        messages.success(request, "Palabra registrada exitosamente.")
        return redirect('listarPalabras')

    return redirect('listarPalabras')

# Eliminar palabra (solo administrador)
@permission_required('PalabraInv.delete_palabrainventada', raise_exception=True)
def eliminarPalabra(request, id):
    palabra = get_object_or_404(PalabraInventada, id=id)
    palabra.delete()
    messages.success(request, "Palabra eliminada correctamente.")
    return redirect('listarPalabras')

# Editar palabra
@login_required
def editarPalabra(request, id):
    palabra = get_object_or_404(PalabraInventada, id=id)
    return render(request, "PalabraInv/editarPalabra.html", {'palabra': palabra})

# Procesar edición
@login_required
def actualizarPalabra(request, id):
    palabra = get_object_or_404(PalabraInventada, id=id)

    if request.method == "POST":
        palabra.palabra = request.POST.get('palabra', '').strip()
        palabra.significado = request.POST.get('significado', '').strip()
        
        if 'imagen' in request.FILES:
            palabra.imagen = request.FILES['imagen']
            
        palabra.save()
        messages.success(request, "Palabra actualizada correctamente.")
        return redirect('listarPalabras')

    return redirect('listarPalabras')

def calendarioPalabras(request):
    return render(request, "PalabraInv/calendario.html")

def eventosPalabras(request):
    palabras = PalabraInventada.objects.select_related('creador').all()
    eventos = []

    for palabra in palabras:
        eventos.append({
            'title': f"{palabra.palabra} ({palabra.creador.username})",
            'start': palabra.fecha_creacion.strftime('%Y-%m-%d'),
            'color': '#3498db'  # color base
        })

    return JsonResponse(eventos, safe=False)