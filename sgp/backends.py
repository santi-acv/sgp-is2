"""
Los backends de autorización manejan el proceso de autenticación. En esta
aplicación se utilizacan dos de ellos: un backend personalizado que autentica
a los usuarios utilizando el servicio de identidad de google, y el backend de
la librería ``django-guardian`` que permite asignar permisos a instancias
individuales de modelos.
"""

from django.contrib.auth.backends import ModelBackend

from google.oauth2 import id_token
from google.auth.transport import requests

from .models import User


CLIENT_ID = "995502643398-16c9uqsedvqktsolf042evsqqij1m9ks.apps.googleusercontent.com"


class OAuth2Backend(ModelBackend):
    """
    Autentica el usuario usando la librería OAuth 2.0 de Google.\n
    Fecha: 21/08/21\n
    Artefacto: Usuario
    """

    def authenticate(self, request, token=None, test=False, **kwargs):
        """
        Verifica la validez del token de ID y autentica al usuario.

        Extrae la ID del usuario del token y comprueba si este existe en la
        base de datos. Si no, también extrae sus datos personales y crea una
        instancia del modelo User. Si el token es inválido, el procso falla.

        Si el parámetro test es falso, ignora el proceso de validación y acepta
        el parámetro token como la id del usuario, iniciando su sesión. Esto se
        utiliza al realizar las pruebas unitarias.

        :param request: Sesión que será autenticada si el token es válido.
        :param token: Token a ser validado.
        :param test: Indica si se está probando el software.
        :type request: request
        :type token: string
        :type test: bool

        Fecha: 21/08/21

        Artefacto: módulo de seguridad
        """
        if test:
            return User.objects.get(user_id=token)
        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
            userid = idinfo['sub']
        except ValueError:
            print("Could not verify token")
            return None
        try:
            user = User.objects.get(user_id=userid)
        except User.DoesNotExist:
            # Crear nuevo usuario
            email = idinfo['email']
            nombre = idinfo['given_name']
            apellido = idinfo['family_name']
            user = User.objects.create_user(userid, email, nombre, apellido)
        return user

    def get_user(self, user_id):
        """
        Comprueba si existe un usuario con esa ID en la base de datos.

        Si existe, lo retorna. Si no, retorna None.

        :param user_id: ID del usuario que se desea comprobar.
        :type user_id: string

        Fecha: 21/08/21

        Artefacto: módulo de seguridad

        |
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
