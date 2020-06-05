FROM mundialis/actinia-core:0.99

# install importer and exporter modules (for ace) to use interface description
RUN grass --tmp-location EPSG:4326 --exec g.extension -s url=https://github.com/mundialis/importer extension=importer && \
grass --tmp-location EPSG:4326 --exec g.extension -s url=https://github.com/mundialis/exporter extension=exporter

RUN pip3 uninstall actinia-gdi.wsgi -y

COPY docker/actinia-core/actinia.cfg /etc/default/actinia

WORKDIR /src/actinia-gdi
