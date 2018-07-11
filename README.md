# Brain Image Library - Django Site

## Prerequisites for Production (CentOS 7)

You'll need to install python3, nginx, gunicorn, and postgresql.

Run the following command to set up postgres:

    sudo postgresql-setup initdb

Create `gunicorn.service` in `/etc/systemd/system/gunicorn.service`:

    [Unit]
    Description=gunicorn daemon
    After=network.target

    [Service]
    User=<username>
    Group=<groupname>
    WorkingDirectory=<top_level_path>/bil_site
    ExecStart=<top_level_path>/bil_site/bil_site_venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:<top_level_path>/bil_site/bil_site.sock bil_site.wsgi

    [Install]
    WantedBy=multi-user.target

Be sure to change any of the values listed in angle brackets like `User` and
`Group`.

In your nginx conf file, add the following to the `server` section:

    server {
        listen <port number;
        server_name <host_name>;

        location = /favicon.ico { access_log off; log_not_found off; }
        location /static/ {
            root <top_level_dir>/bil_site;
        }

        location / {
            proxy_set_header Host $http_host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_pass http://unix:<top_level_dir>/bil_site/bil_site.sock;
        }
    }

Once again, you'll need to change the options in angle brackets.

Make sure the following packages are running and enabled at startup:

    sudo systemctl start postgresql
    sudo systemctl start nginx
    sudo systemctl start gunicorn
    sudo systemctl enable postgresql
    sudo systemctl enable nginx
    sudo systemctl enable gunicorn

## Installation and Setup

To set up the website locally for the first time, do the following:

    python3 -m venv bil_site_venv
    source bil_site_venv/bin/activate
    pip install -r requirements.txt

You need to create a file called `site.cfg` file in the main directory, which
will store the secret key and various other secret or server specific settings.
You can see an example in `example.cfg`. You *must* generate a new secret key
when using this site in production, which you can do like this:

    cp example.cfg site.cfg
    python manage.py shell -c 'from django.core.management import utils; print(utils.get_random_secret_key())'

In site.cfg, replace the value associated `SECRET_KEY` with the value you
generated from the previous command. Note: certain characters will throw off
the config parser. The easiest thing to do is to just generate a different key.

You'll also want to change `IMG_DATA_USER` to whatever PSC username you have on
DXC. You could also change the `IMG_DATA_HOST` to say your local machine for
offline testing. This assumes a passwordless authentication like using [ssh
keys](https://linuxconfig.org/passwordless-ssh). The way remote directory
creation/destruction/management will work in production is still being
determined. It likely will be handled by one account that manages the
appropriate permissions.

Next, we'lll set up the database and create a super user:

    python manage.py makemigrations
    python manage.py migrate --run-syncdb
    python manage.py createsuperuser

You also need to install rabbitMQ, which is pretty easy if you're using Ubuntu:

    sudo apt-get install rabbitmq-server

## Serving the Django Site (in development)

In one terminal, start Celery and leave it running while the server is up:

    celery -A bil_site worker -l info

In a separate terminal, start Django itself:

    python manage.py runserver

Make sure the python virtual environment is active in both terminals. You can
activate it by typing:

    source bil_site_venv/bin/activate

If the server is successfully running, navigate your browser to
[127.0.0.1:8000](127.0.0.1:8000).

Now that you've created your virtual environment, you should usually only have
to run these two commands in the future:

    source bil_site_venv/bin/activate
    python manage.py runserver

Note: you only have to run the `source` command again if you open a different
terminal or explicitly `deactivate`.

## Serving the Django Site (in development)

## Updating the Site

If you ever change the models, you'll likely have to re-run the migrate
commands:

    python manage.py makemigrations
    python manage.py migrate --run-syncdb

## Notes
Currently, when a collection is created, a fake staging area is 
created for the collection. This option can be changed in site.cfg 
(FAKE_STORAGE_AREA) when hosting the server. Once the website is 
deployed, this option will be 
changed so that the path reflects where the collection will actually 
be stored. 
