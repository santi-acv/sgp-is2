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

    def authenticate(self, request, token=None, **kwargs):
        """
        Verifica la validez del token de ID y extrae los datos del usuario.\n
        Si el usuario no existe en la base de datos, crea una entrada.\n
        Fecha: 21/08/21\n
        Artefacto: Usuario
        """
        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
            userid = idinfo['sub']
            email = idinfo['email']
            nombre = idinfo['given_name']
            apellido = idinfo['family_name']
        except ValueError:
            print("Could not verify token")
            return None
        try:
            user = User.objects.get(user_id=userid)
        except User.DoesNotExist:
            # Crear nuevo usuario
            user = User.objects.create_user(userid, email, nombre, apellido)
        return user

    def get_user(self, user_id):
        """
        Comprueba si el usuario existe.\n
        Fecha: 21/08/21\n
        Artefacto: Usuario
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
