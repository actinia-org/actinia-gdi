# We use Jinja!
(http://jinja.pocoo.org/docs/2.10/templates/)

### To create API responses:
* **render_template** from flask which is based on jinja (http://flask.pocoo.org/docs/0.12/tutorial/templates/)
* call loader with
```
app.jinja_env.loader.get_source(app.jinja_env,'folderInTemplates/template.json')
```

### To create requests for GeoNetwork:
  * .xml file templates for HTTP POST requests
  * .json file templates for HTTP GET key-value-pairs
  * Create loader. If imported as module, use it like this:
  ```
  loader=PackageLoader('templates', '')
  ```
  e.g. when app.run(use_reloader=True)
  * Create loader with autoescape:
  ```
  # keep autoescape? at least in mind ...
  tplEnv = Environment(
        loader=PackageLoader('actinia_gdi', 'templates'),
        autoescape=select_autoescape(['html', 'xml']),
        trim_blocks=True,
        lstrip_blocks=True
   )
  ```
  http://flask.pocoo.org/docs/1.0/templating/#controlling-autoescaping
