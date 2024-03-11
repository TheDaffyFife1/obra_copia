from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import Group
from .roles import ADMIN_ROLE, RH_ROLE, USER_ROLE
from .models import UserProfile,Obra,Empleado,Puesto
from django.contrib.auth.decorators import login_required
from .RegistrationForm import RegistrationForm
from django.contrib.auth import login
from django.db import IntegrityError
from django.http import HttpResponseForbidden, HttpResponseRedirect
from .RegistrationObra import ObraForm
from django.urls import reverse
from .FormAsignarObra import AsignarObraForm
from .FormEmpleado import EmpleadoForm
from django.core.serializers import serialize
import json

@login_required
def accesos(request):
    # Asumiendo que los roles son variables globales o están importados correctamente
    role = request.user.userprofile.role
    if role == ADMIN_ROLE:
        return redirect('admin_dashboard')
    elif role == RH_ROLE:
        return redirect('rh_dashboard')
    
    elif role == USER_ROLE:
        return redirect('user_asistencia')
    else:
        # Puedes redirigir a una página de error o a la página de inicio, etc.
        return redirect('default_page')
    
@login_required
def admin_dashboard(request):
    if request.user.userprofile.role != ADMIN_ROLE:
        return HttpResponseForbidden("No tienes permiso para ver esta página.")
    return render(request, 'admin_dashboard.html')

@login_required
def rh_dashboard(request):
    user_profile = request.user.userprofile
    if user_profile.role == RH_ROLE:
        # Asumiendo que 'obra_id' es un campo en el modelo de UserProfile para el ID de la obra.
        obra_id = user_profile.obra_id
        if obra_id:
            obra = get_object_or_404(Obra, id=obra_id)
            # Puedes pasar 'obra' al contexto si la plantilla necesita mostrar información sobre la obra
            return render(request, 'rh_dashboard.html', {'obra': obra})
        else:
            # Manejar el caso de que no haya un ID de obra asociado
            return HttpResponseForbidden("Este usuario de RH no tiene una obra asignada.")
    else:
        return HttpResponseForbidden("No tienes permiso para ver esta página.")

@login_required
def crear_empleado(request):
    user_profile = request.user.userprofile
    if user_profile.role == RH_ROLE:
        obra_id = user_profile.obra_id
        if obra_id:
            if request.method == 'POST':
                form = EmpleadoForm(request.POST, request.FILES)
                if form.is_valid():
                    empleado = form.save(commit=False)
                    if not empleado.pk:  # Si es un nuevo empleado
                        empleado.sueldo = empleado.puesto.sueldo_base
                    empleado.obra_id = obra_id  # Asegúrate de asignar la obra correcta
                    empleado.save()
                    return redirect('lista_empleados')
            else:
                form = EmpleadoForm()
            
            # Obtén los sueldos base de todos los puestos y conviértelos en un diccionario de Python
            sueldos_base = {str(puesto.id): str(puesto.sueldo_base) for puesto in Puesto.objects.all()}
            # Convierte el diccionario de sueldos base a JSON
            sueldos_base_json = json.dumps(sueldos_base)
            
            return render(request, 'registro_empleados.html', {
                'form': form,
                'sueldos_base': sueldos_base_json,  # Pasa sueldos_base como JSON al template
            })
        else:
            return HttpResponseForbidden("Este usuario de RH no tiene una obra asignada.")
    else:
        return HttpResponseForbidden("No tienes permiso para ver esta página.")
    

@login_required
def user_asistencia(request):
    user_profile = request.user.userprofile
    if user_profile.role == USER_ROLE:
        obra_id = user_profile.obra_id
        if obra_id:
            obra = get_object_or_404(Obra, id=obra_id)
            # La lógica para mostrar la asistencia del usuario en la obra
            return render(request,'user_asistencia.html', {'obra': obra})
        else:
            # Manejar el caso de que no haya un ID de obra asociado
            return HttpResponseForbidden("Este usuario no tiene una obra asignada.")
    else:
        return HttpResponseForbidden("No tienes permiso para ver esta página.")

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                # Intenta crear el usuario y su perfil de usuario correspondiente
                user = form.save()  # Guarda la información del usuario
                user.refresh_from_db()  # Carga la instancia del usuario recién creada

                # Establece los atributos adicionales del usuario aquí si es necesario
                # user.profile.some_attribute = 'some_value'
                
                user.save()  # Guarda los cambios en el objeto de usuario

                # Verifica si ya existe un UserProfile para el usuario
                if not UserProfile.objects.filter(user=user).exists():
                    role = form.cleaned_data.get('role')
                    UserProfile.objects.create(user=user, role=role)  # Crea el perfil de usuario con el rol

                    login(request, user)  # Inicia sesión del usuario
                    return redirect('accesos')  # Redirecciona según el rol del usuario
                else:
                    # Si el UserProfile ya existe, podrías redireccionar al usuario a una página de error o de inicio
                    # O mostrar un mensaje de error en la misma página de registro
                    form.add_error(None, 'El usuario ya tiene un perfil asignado.')
            except IntegrityError as e:
                # Añade un mensaje de error al formulario si hay un error de integridad (por ejemplo, un duplicado)
                form.add_error(None, f'Ocurrió un error de integridad: {e}')
            
    else:
        form = RegistrationForm()
    
    return render(request, 'registration/registro.html', {'form': form})

def crear_obra(request):
    """
    Vista para crear una nueva obra. Maneja solicitudes GET para mostrar el formulario y POST para procesar el formulario.
    """
    if request.method == 'POST':
        form = ObraForm(request.POST)
        if form.is_valid():
            form.save()
            # Reemplaza 'lista_obras' con el nombre de la ruta de la vista a la que deseas redirigir
            return redirect('lista_obras')
    else:
        form = ObraForm()  # Inicializa un formulario en blanco para solicitudes GET

    # Renderiza el template con el formulario, sea nuevo o con errores
    return render(request, 'obras/registro_obra.html', {'form': form})

def lista_obras(request):
    """
    Vista para listar todas las obras registradas en la base de datos.
    """
    obras = Obra.objects.all()  # Recupera todas las obras
    return render(request, 'obras/lista_obras.html', {'obras': obras})

def cambiar_estado_obra(request, obra_id):
    obra = Obra.objects.get(id=obra_id)
    obra.activa = not obra.activa
    obra.save()
    return HttpResponseRedirect(reverse('lista_obras'))

def eliminar_obra(request, obra_id):
    Obra.objects.get(id=obra_id).delete()
    return HttpResponseRedirect(reverse('lista_obras'))

def editar_obra(request, obra_id):
    obra = get_object_or_404(Obra, id=obra_id)
    if request.method == 'POST':
        form = ObraForm(request.POST, instance=obra)
        if form.is_valid():
            form.save()
            return redirect('lista_obras')
    else:
        form = ObraForm(instance=obra)
    return render(request, 'obras/editar_obra.html', {'form': form, 'obra': obra})

def asignar_obra_a_usuario(request, user_profile_id):
    user_profile = get_object_or_404(UserProfile, pk=user_profile_id)
    if request.method == 'POST':
        form = AsignarObraForm(request.POST, instance=user_profile)
        if form.is_valid():
            # Asegúrate de que el usuario es RH o User antes de guardar
            if user_profile.role in [RH_ROLE, USER_ROLE]:
                form.save()
                return redirect('lista_user_profiles')
            else:
                # Manejar el caso en que el rol no es permitido para la asignación
                pass  # Puedes redirigir o mostrar un mensaje de error
    else:
        form = AsignarObraForm(instance=user_profile)

    return render(request, 'asignar_obra.html', {'form': form, 'user_profile': user_profile})

def lista_user_profiles(request):
    # Si deseas filtrar por roles específicos, puedes hacerlo aquí
    user_profiles = UserProfile.objects.filter(role__in=[RH_ROLE, USER_ROLE])
    return render(request, 'lista_user_profiles.html', {'user_profiles': user_profiles})

@login_required
def lista_empleados(request):
    user_profile = request.user.userprofile
    if user_profile.role == RH_ROLE:
        # Asumiendo que 'obra_id' es un campo en el modelo de UserProfile para el ID de la obra.
        obra_id = user_profile.obra_id
        if obra_id:
            obra = get_object_or_404(Obra, id=obra_id)
            # Puedes pasar 'obra' al contexto si la plantilla necesita mostrar información sobre la obra
            empleados = Empleado.objects.filter(obra_id=obra)
            return render(request, 'lista_empleados.html', {'empleados': empleados, 'obra': obra})
        else:
            # Manejar el caso de que no haya un ID de obra asociado
            return HttpResponseForbidden("Este usuario de RH no tiene una obra asignada.")
    else:
        return HttpResponseForbidden("No tienes permiso para ver esta página.")

