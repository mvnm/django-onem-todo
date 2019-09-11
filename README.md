### Quickstart

Works with Python 3.7. Preferably to work in a virtual environment, use [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io) to create a virtual environment.

1. mkvirtualenv todo --python=`which python 3.7`
2. sudo apt-get install python3.7-dev

1. git clone git@github.com:mvnm/django-onem-todo.git
2. pip install -r requirements.txt
3. python manage.py migrate
4. python manage.py runserver

### Deploy to Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)
