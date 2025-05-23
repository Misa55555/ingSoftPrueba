# applications/dashboard/decorators.py
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def group_required(group_names):
    """
    Decorador que comprueba si un usuario pertenece a alguno de los grupos especificados.
    group_names puede ser un string con un nombre de grupo o una lista de nombres.
    """
    def check_groups(user):
        if isinstance(group_names, str):
            groups = [group_names]
        else:
            groups = list(group_names) # Asegurar que sea una lista

        if user.is_authenticated:
            # Un superusuario tiene todos los permisos y pertenece a todos los grupos implícitamente
            if user.is_superuser:
                return True
            # Comprobar si el usuario pertenece a alguno de los grupos requeridos
            if user.groups.filter(name__in=groups).exists():
                return True
        # Si no cumple, puedes lanzar PermissionDenied o simplemente devolver False
        # Devolver False hará que user_passes_test redirija a LOGIN_URL
        # raise PermissionDenied # Alternativa
        return False
    return user_passes_test(check_groups)

# Ejemplos de cómo podrías crear decoradores específicos si quieres más claridad:
def admin_required(function=None):
    actual_decorator = group_required("Administrador")
    if function:
        return actual_decorator(function)
    return actual_decorator

def empleado_required(function=None):
    actual_decorator = group_required("Empleado")
    if function:
        return actual_decorator(function)
    return actual_decorator