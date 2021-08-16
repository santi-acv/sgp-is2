from django.test import TestCase
from django.urls import reverse


class IndexPageTest(TestCase):

    def test_retorna_respuesta_http(self):
        """
        Verifica si la pagina de inicio envía una respuesta apropiada
        Fecha: 16/08/21
        Artefacto: Página de inicio
        """
        response = self.client.get(reverse('sgp:index'))
        self.assertEqual(response.status_code, 200)

    def test_contiene_titulo_pagina(self):
        """
        Comprueba si la respuesta contiene el nombre de la aplicación
        Fecha: 16/08/21
        Artefacto: Página de inicio
        """
        response = self.client.get(reverse('sgp:index'))
        self.assertContains(response, 'Sistema Gestor de Proyectos')
