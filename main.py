"""main.py

  _   ___             _                                   
 (_) |__ \           | |                                  
  _     ) |  ______  | |_    __ _    __ _    __ _    ___  
 | |   / /  |______| | __|  / _` |  / _` |  / _` |  / _ \ 
 | |  / /_           | |_  | (_| | | (_| | | (_| | | (_) |
 |_| |____|           \__|  \__,_|  \__, |  \__, |  \___/ 
                                     __/ |   __/ |        
                                    |___/   |___/         

"""

import os
import logging
from sanic import Sanic
from raven import Client
from raven.conf import setup_logging
from raven.handlers.logging import SentryHandler
from parsers import FacebookYamlExecutor
from endpoints import fb

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

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 8080)), 
            host=os.environ.get("IP", "0.0.0.0"),
            debug=False,
            workers=4)