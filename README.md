# actinia gdi

You can run actinia-gdi in multiple ways:

* as actinia-core plugin
* as standalone app with gunicorn, connected with a running actinia-core instance

Depending on how you run, it, actinia-gdi has different endpoints as some make only sense in plugin mode or vice versa. See `actinia_gdi/endpoints.py`. Therefore a running postgres instance is only needed in standalone mode. If used as actinia-core plugin, the main.py is not executed. In standalone-mode, GRASS GIS is not required. Therefore, endpoints which needs GRASS GIS access, are only added in plugin-mode.

## Installation
For DEV setup or deployments, see docker/README.md.

## actinia-core process-chain templating
see actinia-module.md

## DEV notes:

### Build

__insprired by https://hynek.me/articles/sharing-your-labor-of-love-pypi-quick-and-dirty/__

to create a shippable wheel, run
```
pip3 install --upgrade pip pep517
python3 -m pep517.build .
```

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
