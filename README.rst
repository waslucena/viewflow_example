0. $ vagrant up
1. $ vagrant ssh
2. python viewflows/manage.py migrate
3. python viewflows/manage.py createsuperuser
4. python viewflows/manage.py runserver 0.0.0.0:8000
5. open http://192.168.33.11:8000/admin/