FROM centos/python-38-centos7

# Overwrite the base image run script to make port configurable
COPY ./s2i/bin/run $STI_SCRIPTS_PATH/

ENV SETUPTOOLS_SCM_PRETEND_VERSION=0.0.1

COPY gunicorn.cfg /gunicorn.cfg
