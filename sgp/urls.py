from django.urls import path
from . import views

app_name = 'sgp'
urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('administrar/', views.administrar, name='administrar'),
    path('crear_proyecto/', views.crear_proyecto, name='crear_proyecto'),
    path('proyecto-<int:proyecto_id>', views.mostrar_proyecto, name='mostrar_proyecto'),
    path('proyecto-<int:proyecto_id>/editar', views.editar_proyecto, name='editar_proyecto'),
    path('proyecto-<int:proyecto_id>/eliminar', views.eliminar_proyecto, name='eliminar_proyecto'),
    path('proyecto-<int:proyecto_id>/roles', views.administrar_roles, name='administrar_roles'),
]
