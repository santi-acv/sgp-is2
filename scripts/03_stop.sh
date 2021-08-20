#!/bin/bash


# Verifica que el script tenga permisos de administrador
if [ "$EUID" -ne 0 ]; then
	echo "El script se debe ejecutar con sudo."
	exit
fi

VAR=''

# Inicia el servicio postgres
if systemctl is-active --quiet postgresql.service; then
	service postgresql stop
	echo "Deteniendo postgres.service..."
	VAR='x'
fi


# Inicia el servicio uWSGI
if systemctl is-active --quiet uwsgi.service; then
	service uwsgi stop
	echo "Deteniendo uwsgi.service..."
	VAR='x'
fi


# Inicia el servicio NGINX
if systemctl is-active --quiet nginx.service; then
	service nginx stop
	echo "Deteniendo nginx.service..."
	VAR='x'
fi

if [ -z $VAR ]; then
	echo "Ningún servicio se encuentra activo."
fi

