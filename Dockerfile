FROM python:3.6

ENV YAML_URL= \
    ACCESS_TOKEN= \
    VF_TOKEN= \
    SENTRY=

WORKDIR /app
COPY . /app
RUN python setup.py install
EXPOSE 8080
ENTRYPOINT [ "taggo" ]