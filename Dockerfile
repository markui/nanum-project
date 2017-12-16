FROM            30siwon/base
MAINTAINER      75220244@naver.com

ENV             LANG C.UTF-8
ENV             DJANGO_SETTINGS_MODULE config.settings.dev

# 현재 위치를 /srv/app 폴더에 복사 및 requirements 설치
COPY            . /srv/app
RUN             /root/.pyenv/versions/app/bin/pip install -r /srv/app/.requirements/dev.txt

# pyenv local 설정
WORKDIR         /srv/app
RUN             pyenv local app

# Nginx
RUN             cp /srv/app/.config/dev/nginx/nginx.conf \
                    /etc/nginx/nginx.conf
RUN             cp /srv/app/.config/dev/nginx/app.conf \
                    /etc/nginx/sites-available/
RUN             rm -rf /etc/nginx/sites-enabled/*
RUN             ln -sf /etc/nginx/sites-available/app.conf \
                        /etc/nginx/sites-enabled/app.conf

# uWSGI
RUN             mkdir -p /var/log/uwsgi/app

# RabbitMQ
RUN             apt-get -y update
RUN             apt-get install -y rabbitmq-server

# manage.py
WORKDIR         /srv/app/nanum
RUN             /root/.pyenv/versions/app/bin/python manage.py collectstatic --noinput
RUN             /root/.pyenv/versions/app/bin/python manage.py migrate --noinput

# supervisor
RUN             cp /srv/app/.config/dev/supervisor/* \
                    /etc/supervisor/conf.d/
CMD             supervisord -n

EXPOSE          80
