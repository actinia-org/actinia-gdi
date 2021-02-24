# We use Jinja!
(http://jinja.pocoo.org/docs/2.10/templates/)

### To create API responses:
* **render_template** from flask which is based on jinja (http://flask.pocoo.org/docs/0.12/tutorial/templates/)
* call loader with
```
app.jinja_env.loader.get_source(app.jinja_env,'folderInTemplates/template.json')
```
