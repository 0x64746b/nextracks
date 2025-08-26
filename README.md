# Nextracks

Visualize GPX tracks shared via Nextcloud.

## Deployment

Exemplary [Supervisor](https://supervisord.org/) config:

```ini
[program:nextracks]
environment=NEXTRACKS_NC_DOMAIN=<your.nextcloud.tld>,PYTHONUNBUFFERED=TRUE
directory=%(ENV_HOME)s/www/nextracks
command=%(ENV_HOME)s/www/nextracks/.venv/bin/gunicorn --config %(ENV_HOME)s/www/nextracks/conf.py
startsecs=30
```

And a stub for the [Gunicorn](https://gunicorn.org/) config referenced above:

```python
import os
app_path = os.environ['HOME'] + '/www/nextracks'

# Gunicorn configuration
wsgi_app = 'api:app'
bind = ':8000'
chdir = app_path
workers = 4
worker_class = 'uvicorn.workers.UvicornWorker'
accesslog = os.environ['HOME'] + '/logs/nextracks/access.log'
errorlog = os.environ['HOME'] + '/logs/nextracks/error.log'
capture_output = True
```
