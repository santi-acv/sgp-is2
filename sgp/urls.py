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
    path('proyecto-<int:proyecto_id>/roles', views.administrar_roles, name='administrar_roles'),
    path('proyecto-<int:proyecto_id>/roles/importar', views.importar_roles, name='importar_roles'),
    path('proyecto-<int:proyecto_id>/roles/exportar', views.exportar_roles, name='exportar_roles'),
    path('proyecto-<int:proyecto_id>/equipo', views.administrar_equipo, name='administrar_equipo'),
    path('proyecto-<int:proyecto_id>/product-backlog', views.product_backlog, name='product_backlog'),
    path('proyecto-<int:proyecto_id>/crear-user-story', views.crear_user_story, name='crear_user_story'),
    path('proyecto-<int:proyecto_id>/us-<int:us_numero>', views.mostrar_user_story, name='mostrar_user_story'),
    path('proyecto-<int:proyecto_id>/us-<int:us_numero>/editar', views.editar_user_story, name='editar_user_story'),
    path('proyecto-<int:proyecto_id>/crear-sprint', views.crear_sprint, name='crear_sprint'),
    path('proyecto-<int:proyecto_id>/sprint-<int:sprint_id>', views.mostrar_sprint, name='mostrar_sprint'),
    path('proyecto-<int:proyecto_id>/sprint-<int:sprint_id>/editar', views.editar_sprint, name='editar_sprint'),
    path('proyecto-<int:proyecto_id>/sprint-<int:sprint_id>/equipo', views.equipo_sprint, name='equipo_sprint'),
    path('proyecto-<int:proyecto_id>/sprint-<int:sprint_id>/backlog', views.sprint_backlog, name='sprint_backlog'),
    path('proyecto-<int:proyecto_id>/planificacion', views.planificacion, name='planificacion'),
    path('proyecto-<int:proyecto_id>/kanban', views.kanban, name='kanban'),
    path('proyecto-<int:proyecto_id>/kanban/registro', views.registro_kanban, name='registro_kanban'),
    path('proyecto-<int:proyecto_id>/sprint-<int:sprint_id>/burndown-chart', views.burndown, name='burndown_chart'),
    path('proyecto-<int:proyecto_id>/reportes/product-backlog', views.reporte_proyecto, name='reporte_proyecto'),
    path('proyecto-<int:proyecto_id>/reportes/sprint-<int:sprint_id>', views.reporte_sprint, name='reporte_sprint'),
    path('proyecto-<int:proyecto_id>/reportes/us-prioridad', views.reporte_us_prioridad, name='reporte_us_prioridad'),
    path('proyecto-<int:proyecto_id>/historial', views.historial_modificaciones, name='historial_modificaciones'),
]
