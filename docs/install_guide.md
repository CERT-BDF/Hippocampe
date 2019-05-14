# Install Guide

## Intro
You will find bellow the installation instructions.
Don't want to install it ? You can use the docker version instead, check [this](#docker).
Check also the [tutorial](tutorial.md) for more details.

## Requirements

Hippocampe needs some external tools to work, you will find below the list of requirements:

+ JAVA (either [Oracle](http://www.webupd8.org/2014/03/oracle-java-8-stable-released-install.html) or [openJDK](http://openjdk.java.net/install/index.html), however we have noticed better performance with oracle)
+ [Elasticsearch **5.1**](https://www.elastic.co/guide/en/elasticsearch/reference/current/deb.html)
 + Some python libraries:
    + elasticsearch
    + Configparser
    + flask
    + python-dateutil
    + apscheduler
    + requests

```
pip install elasticsearch Configparser netaddr flask python-dateutil apscheduler requests
```

## Configuration

The default Elasticsearch 5.1's configuration is enough to make Hippocampe works.

## Installation
* Clone or download the project
* Install the web dependencies with bower (https://bower.io/)
```
cd hippocampe/core/static
bower install
```
* Start elasticsearch
```
service elasticsearch start
```
* run app.py script   
```
python hippocampe/core/app.py
```
By default, Hippocampe is listening on port 5000.

## Docker
If you just want to give it a try, you may want to use Hippocampe inside of Docker:

```
cd hippocampe/
docker build -t hippocampe .
docker run -p 5000:5000 hippocampe
```

Now Hippocampe is available on port 5000 and runs inside a docker.

If you want to spin-up both Elasticsearch and Hippocampe, you can use docker-compose:

**Note:** If you use this method, you need to edit core/conf/hippo/hippo.conf and change the elasticsearch address to the container name
```
[elasticsearch]
ip : hipposearch
port : 9200
```
```
cd hippocampe/
docker-compose up
```


## Hippocampe as a service

To turn Hippocampe into a service, the uWSGI tool and a NGINX server will be used.

NGINX will host all the web content while uWSGI will execute the python code.

In this example, Hippocampe is located at ```/opt/hippocampe``` and configuration files for both nginx and uWSGI are located at ```/var/www/demoapp```.

### Install NGINX

```
sudo apt-get install nginx
```

### Install uWSGI

```
sudo apt-get install build-essential python python-dev
sudo pip install uwsgi
```

### Configuring nginx

* Delete the default nginx's site

```
sudo rm /etc/nginx/sites-enabled/default
```

* Create the nginx's configuration file at ```/var/www/demoapp/hippo_nginx.conf```

```
sudo mkdir /var/www/demoapp
```

```
server {
    listen      80;
    server_name localhost;
    charset     utf-8;
    client_max_body_size 75M;

    location / { try_files $uri @hippocampe; }
    location @hippocampe {
        include uwsgi_params;
        uwsgi_pass unix:/var/www/demoapp/demoapp_uwsgi.sock;
    }
}
```

* Link the file with nginx

```
sudo ln -s /var/www/demoapp/hippo_nginx.conf /etc/nginx/conf.d/
sudo /etc/init.d/nginx restart
```

### Configuring uWSGI

* Create the configuration file at ```/var/www/demoapp/demoapp_uwsgi.ini```

```
[uwsgi]
#application's base folder
chdir = /opt/hippocampe/core

#python module to import
app = app
module = %(app)

processes = 8
thread = 16
enable-threads = true
pythonpath = /usr/local/lib/python2.7/dist-packages
pythonpath = /usr/lib/python2.7

#socket file's location
socket = /var/www/demoapp/%n.sock

#permissions for the socket file
chmod-socket    = 666

#the variable that holds a flask application inside the module imported at line #6
callable = app

#location of log files
logto = /var/www/demoapp/log/uwsgi/%n.log
uid = www-data
gid = www-data
```

* Create the folder for uWSGI's logs

```
sudo mkdir -p /var/www/demoapp/log/uwsgi
```

* Give the adequat rights

```
sudo chown -R www-data:www-data /var/www/demoapp/
sudo chown -R www-data:www-data /opt/hippocampe
```

### Turn all stuff into a service with ```systemctl```

* Create the file ```/etc/systemd/system/uwsgi.service```

```
[Unit]
Description=uWSGI for hippocampe demo
After=syslog.target

[Service]
ExecStart=/usr/local/bin/uwsgi --master --emperor /etc/uwsgi/vassals --die-on-term --uid www-data --gid www-data --logto /var/www/demoapp/log/uwsgi/emperor.log
Restart=always
KillSignal=SIGQUIT
Type=notify
StandardError=syslog
NotifyAccess=all

[Install]
WantedBy=multi-user.target
```

* Create the directory ```/etc/uwsgi/vassals```

```
sudo mkdir -p /etc/uwsgi/vassals
```

* Link the uWSGI config file to it

```
sudo ln -s /var/www/demoapp/demoapp_uwsgi.ini /etc/uwsgi/vassals
```

* Start the service

```
sudo systemctl daemon-reload
sudo systemctl start uwsgi
```

### Test it

Go to ```http://localhost/hippocampe``` and it should work.

Moreover the API is now expose to port 80.

### Logs path

* Hippocampe's logs
   * ```hippocampe/core/logs/hippocampe.log```
* nginx's logs
   * ```/var/log/nginx/access.log```
   * ```/var/log/nginx/error.log```
* uWSGI's logs
   * ```/var/www/demoapp/log/uwsgi/demoapp_uwsgi.log```
   * ```/var/www/demoapp/log/uwsgi/emperor.log```
