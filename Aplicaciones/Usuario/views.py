import random
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required

# Diccionario temporal para almacenar códigos de verificación
codigos_temporales = {}

def vista_login(request):
    if request.method == 'POST':
        identifier = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        try:
            user_obj = User.objects.get(email=identifier)
            username = user_obj.username
        except User.DoesNotExist:
            username = identifier

        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            messages.success(request, f'¡Bienvenido de nuevo, {user.username}!')
            return redirect('/PalabraInv/')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
            return redirect('login')

    return render(request, 'Usuario/login.html')

def registro(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        # Validaciones básicas
        if not username or not email or not password:
            messages.warning(request, 'Todos los campos son obligatorios.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya existe.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'El correo electrónico ya está registrado.')
        else:
            # Crear el usuario
            nuevo_usuario = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # Asignar al grupo "Creador" (ajusta según tu necesidad)
            try:
                grupo_creador = Group.objects.get(name='Creador')
                nuevo_usuario.groups.add(grupo_creador)
            except Group.DoesNotExist:
                messages.warning(request, "El grupo 'Creador' no está creado aún.")

            messages.success(request, 'Registro exitoso. Ahora puedes iniciar sesión.')
            return redirect('login')

    return render(request, 'Usuario/registro.html')

def recuperar_contrasena(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        
        try:
            user = User.objects.get(email=email)
            
            # Generar código de 6 dígitos
            codigo = str(random.randint(100000, 999999))
            codigos_temporales[email] = codigo
            
            # Enviar correo con el código
            send_mail(
                'Recuperación de contraseña - PalabrasInventadas',
                f'Tu código de recuperación es: {codigo}\n\nIngresa este código en la página de recuperación para continuar con el proceso.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            messages.success(request, 'Se ha enviado un código de verificación a tu correo electrónico.')
            return redirect('validar_codigo', email=email)
            
        except User.DoesNotExist:
            messages.error(request, 'No existe una cuenta asociada a este correo electrónico.')
    
    return render(request, 'Usuario/recuperar_contrasena.html')

def validar_codigo(request, email):
    if request.method == 'POST':
        codigo_usuario = request.POST.get('codigo', '').strip()
        codigo_correcto = codigos_temporales.get(email, None)
        
        if codigo_correcto and codigo_usuario == codigo_correcto:
            return redirect('nueva_contrasena', email=email, codigo=codigo_usuario)
        else:
            messages.error(request, 'Código incorrecto. Inténtalo de nuevo.')
    
    return render(request, 'Usuario/validar_codigo.html', {'email': email})

def nueva_contrasena(request, email, codigo):
    # Verificar que el código sea correcto antes de permitir cambiar la contraseña
    codigo_correcto = codigos_temporales.get(email, None)
    if codigo != codigo_correcto:
        messages.error(request, 'Código de verificación inválido.')
        return redirect('login')
    
    if request.method == 'POST':
        nueva_password = request.POST.get('nueva_password', '')
        confirmar_password = request.POST.get('confirmar_password', '')
        
        if nueva_password != confirmar_password:
            messages.error(request, 'Las contraseñas no coinciden.')
        elif len(nueva_password) < 6:
            messages.error(request, 'La contraseña debe tener al menos 6 caracteres.')
        else:
            try:
                user = User.objects.get(email=email)
                user.password = make_password(nueva_password)
                user.save()
                
                # Eliminar el código ya usado
                if email in codigos_temporales:
                    del codigos_temporales[email]
                
                messages.success(request, 'Contraseña actualizada correctamente. Ahora puedes iniciar sesión.')
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, 'Usuario no encontrado.')
    
    return render(request, 'Usuario/nueva_contrasena.html', {'email': email, 'codigo': codigo})
