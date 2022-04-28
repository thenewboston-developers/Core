FROM python:3.10.4-buster AS core

WORKDIR /opt/project

EXPOSE 8000

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH .
ENV CORESETTING_IN_DOCKER true

# TODO(dmu) LOW: Optimize images size by deleting no longer needed files after installation
# We added build-essential to avoid hard to track issues later if add some package that requires it.
# Need to remove it later (when we stabilize list of dependencies) for the sake of image size optimization.
RUN set -xe \
    && apt-get update \
    && apt-get install build-essential \
    && pip install pip==22.0.4 virtualenvwrapper poetry==1.1.13

# For image build time optimization purposes we install depdendencies here (so changes in the source code will not
# require dependencies reinstallation)
COPY ["pyproject.toml", "poetry.lock", "./"]
RUN poetry run pip install pip==22.0.4
RUN poetry install

COPY ["LICENSE", "README.rst", "./"]
COPY core core
RUN poetry install  # this installs just the source code itself, since dependencies are installed before

COPY scripts/dockerized-core-run.sh ./run.sh
RUN chmod a+x run.sh

FROM nginx:1.21.6-alpine AS core-reverse-proxy

RUN rm /etc/nginx/conf.d/default.conf
COPY ./core/config/settings/templates/nginx.conf /etc/nginx/conf.d/core.conf
