from django.test import TestCase
from django.urls import reverse


class IndexPageTest(TestCase):

    def test_retorna_respuesta_http(self):
        """
        Verifica si la pagina de inicio envía una respuesta apropiada\n
        Fecha: 16/08/21\n
        Artefacto: Página de inicio
        """
        response = self.client.get(reverse('sgp:index'))
        self.assertEqual(response.status_code, 200,
                         "La página de inicio retornó un error HTTP")

    def test_contiene_titulo_pagina(self):
        """
        Comprueba si la respuesta renderiza un template del proyecto.\n
        Fecha: 16/08/21\n
        Artefacto: Página de inicio
        """
        response = self.client.get(reverse('sgp:index'))
        self.assertContains(response, 'Sistema Gestor de Proyectos',
                            msg_prefix="La página de inicio no menciona el SGP")
