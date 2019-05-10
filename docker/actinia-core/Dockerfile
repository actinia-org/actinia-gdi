FROM mundialis/actinia-core:latest

ENV SETUPTOOLS_SCM_PRETEND_VERSION=0.1

ARG SOURCE_GIT_URL=https://github.com
ARG SOURCE_GIT_REMOTE=mundialis
ARG SOURCE_GIT_REPO=actinia-gdi
ARG SOURCE_GIT_BRANCH=master

# Install actinia-gdi
WORKDIR /src
ADD https://api.github.com/repos/$SOURCE_GIT_REMOTE/$SOURCE_GIT_REPO/git/refs/heads/$SOURCE_GIT_BRANCH version.json
RUN git clone -b ${SOURCE_GIT_BRANCH} --single-branch ${SOURCE_GIT_URL}/${SOURCE_GIT_REMOTE}/${SOURCE_GIT_REPO}.git actinia-gdi

WORKDIR /src/actinia-gdi
RUN pip3 install -r requirements.txt
RUN python3 setup.py install

COPY actinia-gdi.cfg /src/actinia-gdi/config/mount/actinia-gdi.ini
RUN rm /src/actinia-gdi/config/mount/sample.ini
COPY actinia.cfg /etc/default/actinia
COPY start.sh /src/start.sh
COPY start-dev.sh /src/start-dev.sh

ENTRYPOINT ["/bin/bash"]
CMD ["/src/start.sh"]

ENV GISBASE ""

EXPOSE 8088
EXPOSE 9191
