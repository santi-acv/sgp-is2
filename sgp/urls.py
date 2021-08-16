from django.urls import path

from . import views

app_name = 'sgp'
urlpatterns = [
    path('', views.index, name='index'),
]
