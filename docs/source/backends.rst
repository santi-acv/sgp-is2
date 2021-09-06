Backends de autorización
========================

Los backends de autorización manejan el proceso de autenticación. En esta
aplicación se utilizacan dos de ellos: un backend personalizado que autentica
a los usuarios utilizando el servicio de identidad de google, y el backend de
la librería ``django-guardian`` que permite asignar permisos a instancias
individuales de modelos.

.. autoclass:: sgp.backends.OAuth2Backend
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members: save

.. note::
   Si desea obtener información sobre el backend de la librería
   ``django-guardian``, por favor consulte la documentación de la misma.