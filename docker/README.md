You can run actinia-gdi in multiple ways:

* as actinia-core plugin
* as standalone app with gunicorn, connected with a running actinia-core instance

Depending on how you run, it, actinia-gdi has different endpoints as some make only sense in plugin mode or vice versa. See `actinia_gdi/endpoints.py`. Therefore a running postgres instance is only needed in standalone mode. If used as actinia-core plugin, the main.py is not executed.


# As actinia-core plugin

To run actinia-gdi with actinia-core, run
```
docker-compose --file docker/docker-compose-plugin.yml build
docker-compose --file docker/docker-compose-plugin.yml up
```

For actinia-gdi development, run and enter the running container.
```
docker-compose --file docker/docker-compose-plugin.yml run --rm \
  --service-ports -w /src/actinia-gdi --entrypoint bash \
  -v $HOME/repos/actinia/actinia-gdi/actinia_gdi:/src/actinia-gdi/actinia_gdi actinia-core
```

And run the actinia-core server with your mounted source code:
```
python3 setup.py install
bash /src/start-dev.sh

# python3 -m actinia_core.main
gunicorn -b 0.0.0.0:8088 -w 1 actinia_core.main:flask_app
```


To also debug inside of actinia-core, also mount the source code:
```
docker-compose --file docker/docker-compose-plugin.yml run --rm \
  --service-ports -w /src/actinia-gdi --entrypoint bash \
  -v $HOME/repos/actinia/actinia_core/src:/src/actinia_core/src \
  -v $HOME/repos/actinia/actinia-gdi/actinia_gdi:/src/actinia-gdi/actinia_gdi actinia-core

# inside, run additionally:
cd /src/actinia_core
python3 setup.py install

cd /src/actinia-gdi
python3 setup.py install

```

If you have problems with cache, run
```
python3 setup.py clean --all
```

And test from outside with API calls, e.g.:
```
curl -u actinia-gdi:actinia-gdi 'http://127.0.0.1:8088/api/v1/swagger.json'
```
Inside the container, you can run GRASS with:
```
# Download GRASS GIS test data and put it into a directory
cd /actinia_core/grassdb
wget https://grass.osgeo.org/sampledata/north_carolina/nc_spm_08_grass7.tar.gz && \
     tar xzvf nc_spm_08_grass7.tar.gz && \
     rm -f nc_spm_08_grass7.tar.gz && \
     mv nc_spm_08_grass7 nc_spm_08
cd -

grass /actinia_core/grassdb/nc_spm_08/PERMANENT
```







# As standalone app

First, build an actinia-gdi image with source-2-image. Install source-to-image binary (here v1.1.9 was used) and run:
```
docker build docker/s2i-actinia-gdi-builder -t s2i-actinia-gdi-builder
```
__To update actinia-gdi, run:__
```
s2i build git@github.com:mundialis/actinia-gdi.git s2i-actinia-gdi-builder actinia-gdi -e APP_CONFIG=/gunicorn.cfg

# if you have local actinia-gdi changes, run
# s2i build actinia-gdi s2i-actinia-gdi-builder actinia-gdi -e APP_CONFIG=/gunicorn.cfg

```
__To run actinia-gdi as standalone app, run__
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

# python3 -m actinia_gdi.main
gunicorn -b 0.0.0.0:5000 -w 1 actinia_gdi.wsgi
```

__And test from outside with API calls, e.g.:__
```
curl 'http://127.0.0.1:5000'
```


## dev notes:

As actinia-gdi can be run as actinia-core plugin and standalone, the endpoint
classes inherit either from flask_restful's Resource (standalone + plugin mode) or from the extended actinia-core ResourceBase (only plugin mode).

__build actinia-gdi from checked out s2i image__
```
cd docker/s2i-actinia-gdi-builder/
git clone git@github.com:sclorg/s2i-python-container.git
cd s2i-python-container
make build TARGET=centos7 VERSIONS=3.6
docker build docker/s2i-actinia-gdi-builder/s2i-python-container/3.6 -t s2i-python-container
```


__test process chains in actinia-core:__
```
curl -u actinia-gdi:actinia-gdi 'http://127.0.0.1:8088/api/v1/locations'

JSON=pc.json
curl -u actinia-gdi:actinia-gdi -X POST "http://127.0.0.1:8088/api/v1/locations/nc_spm_08/processing_async_export" \
     -H 'accept: application/json' -H 'Content-Type: application/json' -d @$JSON \
     | json urls.status | xargs curl -u actinia-gdi:actinia-gdi -X GET

curl -u actinia-gdi:actinia-gdi -X POST "http://127.0.0.1:8088/api/v1/locations/mynewlocation" -H 'accept: application/json' -H \
  'Content-Type: application/json' -d '{"epsg": "25832"}'
```
