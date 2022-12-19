check:
	bash check.sh

collectstatic:
	python manage.py collectstatic --noinput

migrate:
	python manage.py migrate

runserver:
	python manage.py runserver 0.0.0.0:8000

dev: check collectstatic migrate runserver
