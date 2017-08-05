"""main.py"""

import os
from sanic import Sanic
from parsers import FacebookYamlExecutor
from endpoints import fb

app = Sanic('taggo')
app.blueprint(fb)

@app.listener('before_server_start')
async def get_global_app_config(app, loop):
    executor = await FacebookYamlExecutor.from_url(os.environ.get("YAML_URL"))
    app.config.update({"command": executor})

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 8080)), host=os.environ.get("IP", "0.0.0.0"))
