Web tools
----------
  
#### Work in progress. Documentation in construction.

Project using Python 3.6

Packages to be installed:
  
    sudo apt install python3-pip 
                   python3-dev 
                   libpq-dev 
                   postgresql 
                   postgresql-contrib 
                   nginx 
                   curl

#### Create a virtualenv
    virtualenv myprojectenv

Install the requirements

    pip3 install -r requirements.txt

Activate environment
    
    source myprojectenv/bin/activate         



#### Creating Database PostgreSQL
Log into an interactive Postgres session by typing:

    sudo -u postgres psql

First, create a database for your project:

    postgres=# CREATE DATABASE biofoundry;

Next, create a database user for our project. Make sure to select a secure password:
    
    postgres=# CREATE USER admin WITH PASSWORD 'password';

Setting database configuration:

    postgres=# ALTER ROLE admin SET client_encoding TO 'utf8';
    postgres=# ALTER ROLE admin SET default_transaction_isolation TO 'read committed';
    postgres=# ALTER ROLE admin SET timezone TO 'UTC';

Grant privilegies to admin:

    postgres=# GRANT ALL PRIVILEGES ON DATABASE biofoundry TO admin;

Close prompt
    
    postgres=# \q


##### Django project
###### Edit settings.py

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'biofoundry',
            'USER': 'admin',
            'PASSWORD': 'password',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }

###### Migrations
    python3 manage.py makemigrations
    python3 manage.py migrate 

###### Add superuser
    python3 manage.py createsuperuser

=======
    

Web tools is developed by Flavia Araujo for the Concordia Genome Foundry released on Github under the MIT license.

