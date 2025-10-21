FROM python:3
COPY .  /usr/src/app
WORKDIR /usr/src/app
RUN pip install -r requirements.txt
RUN python manage.py collectstatic --noinput
CMD ["gunicorn", "hub.wsgi:application", "-b", "0.0.0.0:8000"]
