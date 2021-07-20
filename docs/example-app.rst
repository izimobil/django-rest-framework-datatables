The example app
===============

django-rest-framework-datatables comes with an example application (the Rolling Stone top 500 albums of all time).
It's a great start for understanding how things work, you can play with several options of Datatables, modify the python code (serializers, views) and test a lot of possibilities.

We encourage you to give it a try with a few commandline calls:

.. code:: bash

    $ git clone https://github.com/izimobil/django-rest-framework-datatables.git
    $ cd django-rest-framework-datatables
    $ pip install -r requirements-dev.txt
    $ python example/manage.py runserver
    $ firefox http://127.0.0.1:8000

A screenshot of the example app:

.. image:: _static/screenshot.jpg

Postgres
########

You can use Postgres as the source database.  To do this, you will need to have `Docker <https://docker.com/>`_ installed.

Initialise the database as follows:

.. code:: bash

  $ export DRFDT_TEST_TYPE=postgres
  $ export DRFDT_POSTGRESQL_USER=pguser
  $ export DRFDT_POSTGRESQL_PASSWORD=pguserpass
  $ export DJANGO_SETTINGS_MODULE=example.settings

  $ # start a local postgres instance
  $ docker-compose -f example/pg/docker-compose.yml up -d

  $ python example/manage.py migrate
  $ python example/manage.py test

  $ # only required if you want to login to the Admin site
  $ python example/manage.py createsuperuser --username admin  --email=email@example.com

  $ # load test data
  $ python example/manage.py loaddata test_data

  $ # shutdown the db (append -v to remove the data volume and delete all data)
  $ docker-compose -f example/pg/docker-compose.yml down