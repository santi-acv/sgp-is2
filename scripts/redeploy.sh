#!/bin/bash

# Define script para poblar la base de datos
DATABASE_SCRIPT="scripts/poblar_base_de_datos.py"

# Obtiene el nombre del ambiente a utilizar
if [[ "$2" == "desarrollo" ]]; then
	AMBIENTE="development"
else
	AMBIENTE="production"
fi

# Obtiene el directorio del proyecto y el usuario dueño de la carpeta
cd "$(git rev-parse --show-toplevel)"
PR_DIR="$(pwd -P)"
OWNER=$(stat -c '%U' $PR_DIR)

# Conecta al servidor postgres y crea las bases de datos
if ! systemctl is-active --quiet postgresql.service; then
	service postgresql start
fi
sudo -u postgres psql << EOF
CREATE USER is2_sgp WITH PASSWORD 'is2_sgp';
ALTER USER is2_sgp CREATEDB;
DROP DATABASE is2_sgp_$AMBIENTE;
CREATE DATABASE is2_sgp_$AMBIENTE;
EOF

# Realiza la migraciones dentro de la base de datos
source venv/bin/activate
if [[ "$AMBIENTE" == "production" ]]; then
	rm -rf static media
	mkdir -p static media
	python3 manage.py collectstatic --settings=is2.settings.production --noinput
fi
python3 manage.py makemigrations --settings=is2.settings.$AMBIENTE
python3 manage.py migrate --settings=is2.settings.$AMBIENTE

# Puebla la base de datos
if [[ -f "$PR_DIR/$DATABASE_SCRIPT" ]]; then
	python3 manage.py shell --settings=is2.settings.$AMBIENTE << EOF
	exec(open("$PR_DIR/$DATABASE_SCRIPT").read())
EOF
fi
deactivate

# Transfiere posesión de los archivos al dueño de la carpeta
chown -R $OWNER:$OWNER $PR_DIR

# Monta el entorno de desarrollo
if [[ "$AMBIENTE" == "development" ]]; then
	source venv/bin/activate
	python3 manage.py runserver --settings=is2.settings.development
	deactivate

# Monta el entorno de producción
elif [[ "$AMBIENTE" == "production" ]]; then

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
fi
