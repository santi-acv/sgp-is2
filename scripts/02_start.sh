#!/bin/bash


# Verifica que el script tenga permisos de administrador
if [ "$EUID" -ne 0 ]; then
	echo "El script se debe ejecutar con sudo."
	exit
fi

VAR=''

# Inicia el servicio postgres
if ! systemctl is-active --quiet postgresql.service; then
	service postgresql start
	echo "Iniciando postgresql.service..."
	VAR='x'
fi


# Inicia el servicio uWSGI
if ! systemctl is-active --quiet uwsgi.service; then
	service uwsgi start
	echo "Iniciando uwsgi.service..."
	VAR='x'
fi


# Inicia el servicio NGINX
if ! systemctl is-active --quiet nginx.service; then
	service nginx start
	echo "Iniciando nginx.service..."
	VAR='x'
fi

if [ -z $VAR ]; then
	echo "No hace falta iniciar nada."
fi

# imprime la URL de la aplicación
echo "La aplicación se debería estar ejecuatando en http://localhost:80/sgp"

