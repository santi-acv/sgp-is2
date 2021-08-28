from django.urls import path

from . import views

app_name = 'sgp'
urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('administrar/', views.administrar, name='administrar'),
    path('proyecto/', views.proyecto, name='proyecto')
]
