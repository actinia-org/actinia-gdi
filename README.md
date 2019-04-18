# actinia gdi

## Requirements
```
sudo apt install \
    python-virtualenv\
    python3\
    python3-dev\
```
* a running GeoNetwork instance
* a running PostgreSQL instance

## DEV - Installation
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
gunicorn -b :5000 actinia_gdi.wsgi
```

If all done, leave environment
```
deactivate
```

## INT - Installation

```
git clone git@github.com:mundialis/actinia-gdi.git
cd actinia-gdi
docker build s2i-actinia-gdi-builder -t s2i-actinia-gdi-builder
s2i build . s2i-actinia-gdi-builder actinia-gdi
docker-compose -f ~/docker/docker-compose.yml up -d actinia-gdi
```

## INT - Update

```
cd actinia-gdi
s2i build . s2i-actinia-gdi-builder actinia-gdi

docker-compose -f ~/docker/docker-compose.yml up -d actinia-gdi
```

## DEV notes:

#### Versioning:

https://semver.org/ (MAJOR.MINOR.PATCH)

#### Logging:
in any module, import `from actinia_gdi.resources.logging import log` and call logger with `log.info("my info i want to log")`


#### requests library

when using requests.post, make sure your postbody is of type 'bytes'. requests automatically counts to set the content-length and might count wrong for strings! `data=bytes(postbody, 'utf-8')`

to debug, use
```
import curlify

log.debug(curlify.to_curl(gnosresp.request))
log.debug(gnosresp.request.headers)
log.debug(gnosresp.content)
```
