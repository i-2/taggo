"""main.py"""

import os
from sanic import Sanic
from parsers import FacebookYamlExecutor
from endpoints import fb

app = Sanic('taggo')
app.blueprint(fb)

@app.listener('before_server_start')
async def get_global_app_config(app, loop):
    app.executor = await FacebookYamlExecutor.from_url(os.environ.get("YAML_URL"))

if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT")), host=os.environ.get("IP"), workers=4)
