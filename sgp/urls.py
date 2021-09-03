from django.urls import path
from . import views

app_name = 'sgp'
urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('administrar/', views.administrar, name='administrar'),
    path('crear_proyecto/', views.crear_proyecto, name='crear_proyecto'),
    path('mostrar_proyecto/<int:proyecto_id>', views.mostrar_proyecto, name='mostrar_proyecto'),
    path('editar_proyecto/<int:proyecto_id>', views.editar_proyecto, name='editar_proyecto'),
    path('eliminar_proyecto/<int:proyecto_id>', views.eliminar_proyecto, name='eliminar_proyecto'),
    path('administrar_roles/<int:proyecto_id>', views.administrar_roles, name='administrar_roles'),
    path('administrar_roles/<int:proyecto_id>/<int:extra>', views.administrar_roles, name='administrar_roles'),
]
