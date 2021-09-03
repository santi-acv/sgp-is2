from django.urls import path
from . import views

app_name = 'sgp'
urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('administrar/', views.administrar, name='administrar'),
    path('crear_proyecto/', views.crear_proyecto, name='crear_proyecto'),
    path('proyectos/', views.proyectos, name='proyectos'),
    path('mostrar_proyecto/<proyecto_id>', views.mostrar_proyecto, name='mostrar_proyecto'),
    path('administrar_roles/<proyecto_id>', views.administrar_roles, name='administrar_roles'),
]
