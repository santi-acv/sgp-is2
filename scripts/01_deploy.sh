#!/bin/bash


# Verifica que el script tenga permisos de administrador
if [ "$EUID" -ne 0 ]; then
	echo "El script se debe ejecutar con sudo."
	exit
fi


# Cambia la ubicacion al directorio del proyecto y almancena la dirección
cd -- "$(dirname "$0")/.." >/dev/null 2>&1
PR_DIR="$(pwd -P )"


# Halla el usuario dueño de la carpeta
OWNER=$(stat -c '%U' $PR_DIR)


# Instala las dependencias
apt install -y nginx uwsgi uwsgi-plugin-python3 python3-virtualenv libpq-dev


# Conecta a postgres y crea las bases de datos
if ! systemctl is-active --quiet postgresql.service; then
	service postgresql start
fi
sudo -u postgres psql << EOF
CREATE USER is2_sgp WITH PASSWORD 'is2_sgp';
CREATE DATABASE is2_sgp_development;
CREATE DATABASE is2_sgp_production;
EOF


# Crea directorios requeridos con los permisos del usuario
sudo -u $OWNER -s -- << EOF
mkdir -p static media


# Crea el ambiente virtual e instala los modulos necesarios
if ! [ -d venv ]; then
	virtualenv venv
fi
source venv/bin/activate
pip install -r "$PR_DIR/requirements.txt"


# Recolecta los archivos estáticos y migra la base de datos
python3 manage.py collectstatic --settings=is2.settings.production --noinput
python3 manage.py makemigrations --settings=is2.settings.production
python3 manage.py migrate --settings=is2.settings.production
deactivate
EOF


# Configura uWSGI para ejecutar la aplicacióon
cat > /etc/uwsgi/apps-enabled/django.ini << EOF
[uwsgi]
chdir = $PR_DIR
env = DJANGO_SETTINGS_MODULE=is2.settings.production
wsgi-file = is2/wsgi.py
workers = 1
plugins = python3
virtualenv = $PR_DIR/venv

EOF
if ! systemctl is-active --quiet uwsgi.service; then
	service uwsgi start
else
	service uwsgi restart
fi


# Configura NGINX para trabajar con Django
cat > /etc/nginx/sites-enabled/django << EOF
server {
    listen 80;
    server_name localhost;

    location / {
        # django running in uWSGI
        uwsgi_pass unix:///run/uwsgi/app/django/socket;
        include uwsgi_params;
        uwsgi_read_timeout 300s;
        client_max_body_size 32m;
    }

    location /static/ {
       # static files
       alias $PR_DIR/static/;
    }

    location /media/ {
        # media files, uploaded by users
        alias $PR_DIR/media/;
    }
}

EOF
if ! systemctl is-active --quiet uwsgi.service; then
	service nginx start
else
	service nginx restart
fi


# imprime la URL de la aplicación
echo "La aplicación se debería estar ejecuatando en http://localhost:80/sgp"

