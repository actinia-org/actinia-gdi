# actinia-gdi

Actinia-gdi can be run as standalone app with gunicorn, connected with a running actinia-core instance. A running postgres instance is needed.

## Build and run with docker:
First, build an actinia-gdi image with source-2-image. Install source-to-image binary (here v1.1.9 was used) and run:
```
git clone git@github.com:mundialis/actinia-gdi.git
cd actinia-gdi
docker build docker/s2i-actinia-gdi-builder -t s2i-actinia-gdi-builder
```
__To build actinia-gdi, run:__
```
s2i build git@github.com:mundialis/actinia-gdi.git s2i-actinia-gdi-builder actinia-gdi -e APP_CONFIG=/gunicorn.cfg -c

# or if you have local actinia-gdi changes, run
s2i build . s2i-actinia-gdi-builder actinia-gdi -e APP_CONFIG=/gunicorn.cfg -c

```
__To run actinia-gdi, run__
```
docker-compose --file docker/docker-compose.yml up -d
```

__For actinia-gdi development, run and enter the running container:__
```
docker-compose --file docker/docker-compose.yml up -d postgis

docker-compose --file docker/docker-compose.yml run --rm \
  --service-ports -w /opt/app-root/src --entrypoint bash \
  -v $HOME/repos/actinia/actinia-gdi/actinia_gdi:/opt/app-root/src/actinia_gdi actinia-gdi
```

__Inside the container, run the actinia-gdi server with mounted source code:__
```
python3 setup.py install
python3 setup.py test

# python3 -m actinia_gdi.main
gunicorn -b 0.0.0.0:5000 -w 1 --access-logfile=- -k gthread actinia_gdi.wsgi
```

__And test from outside with API calls, e.g.:__
```
curl 'http://127.0.0.1:5000'
```


### dev notes:

__build actinia-gdi from checked out s2i image__
```
cd docker/s2i-actinia-gdi-builder/
git clone git@github.com:sclorg/s2i-python-container.git
cd s2i-python-container
make build TARGET=centos7 VERSIONS=3.6
docker build docker/s2i-actinia-gdi-builder/s2i-python-container/3.6 -t s2i-python-container
```

## Build and run without docker:

### Requirements
```
sudo apt install \
    python-virtualenv\
    python3\
    python3-dev\
```
* a running PostgreSQL instance

### Installation
For local developments outside of docker, it is preferred to run actinia-gdi in a virtual python environment.

Clone repository, create virtual environment and activate it:
```
git clone git@github.com:mundialis/actinia-gdi.git
cd actinia-gdi
virtualenv -p python3 venv
. venv/bin/activate
```

Change configuration in ```config/mount```

Install required Python packages into the virtual environment:
```
pip install -r requirements.txt
python setup.py install
```
Run tests:
```
python setup.py test
```

Run the server for development:
```
python -m actinia_gdi.main
```

Or for production use actinia_gdi.wsgi as WSGI callable:
```
gunicorn -b :5000 -w 1 --access-logfile=- -k gthread actinia_gdi.wsgi

```

If all done, leave environment
```
deactivate
```

## Create API docs
```
wget -O /tmp/actinia-gdi.json http://127.0.0.1:5000/latest/api/swagger.json
```
Run spectacle docker image to generate the HTML documentation
```
docker run -v /tmp:/tmp -t sourcey/spectacle \
  spectacle /tmp/actinia-gdi.json -t /tmp

# or if you have spectacle installed (npm install -g spectacle-docs), run
cd actinia_gdi/static
spectacle /tmp/actinia-gdi.json -t .

# to build all in one file:
spectacle -1 /tmp/actinia-gdi.json -t .
```
beautify css
```
sed -i 's+<link rel="stylesheet" href="stylesheets/spectacle.min.css" />+<link rel="stylesheet" href="stylesheets/spectacle.min.css" />\n    <link rel="stylesheet" href="stylesheets/actinia.css" />+g' index.html
```
