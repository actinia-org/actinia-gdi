FROM mundialis/actinia-core:latest

ENV SETUPTOOLS_SCM_PRETEND_VERSION=0.1

# install importer and exporter modules (for ace) to use interface description
RUN grass --tmp-location EPSG:4326 --exec g.extension -s url=https://github.com/mundialis/importer extension=importer && \
grass --tmp-location EPSG:4326 --exec g.extension -s url=https://github.com/mundialis/exporter extension=exporter

# Install actinia-gdi
COPY . /src/actinia-gdi

WORKDIR /src/actinia-gdi
RUN pip3 install -r requirements.txt
RUN python3 setup.py install

COPY docker/actinia-core/actinia-gdi.cfg /src/actinia-gdi/config/mount/actinia-gdi.ini
RUN rm /src/actinia-gdi/config/mount/sample.ini
COPY docker/actinia-core/actinia.cfg /etc/default/actinia
COPY docker/actinia-core/start.sh /src/start.sh
COPY docker/actinia-core/start-dev.sh /src/start-dev.sh

ENTRYPOINT ["/bin/bash"]
CMD ["/src/start.sh"]

ENV GISBASE ""

EXPOSE 8088
EXPOSE 9191
