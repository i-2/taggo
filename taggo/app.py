import os
import logging
from sanic import Sanic
from raven import Client
from raven.conf import setup_logging
from raven.handlers.logging import SentryHandler
from taggo.parsers import FacebookYamlExecutor
from taggo.endpoints import fb

app = Sanic('taggo')
app.blueprint(fb)
client = Client(os.environ.get("SENTRY"))
log_handler = SentryHandler(client)
log_handler.setLevel(logging.ERROR)
setup_logging(log_handler)

@app.listener('before_server_start')
async def get_global_app_config(app, loop):
    executor = await FacebookYamlExecutor.from_url(os.environ.get("YAML_URL"))
    app.config.update({"command": executor})