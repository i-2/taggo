FROM python:3.6

ENV YAML_URL= \
    ACCESS_TOKEN= \
    VF_TOKEN= \
    SENTRY=

WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt

ENTRYPOINT [ "python" , "-m", "sanic", "main.app", "--worker", "4", "--host", "0.0.0.0"]