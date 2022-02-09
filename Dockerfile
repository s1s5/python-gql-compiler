FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV POETRY_VIRTUALENVS_CREATE=false

RUN groupadd -g 999 app
RUN adduser --no-create-home --uid 999 --ingroup app app

USER root
WORKDIR /opt/app
COPY pyproject.toml poetry.lock /opt/app/

RUN python -c "import urllib.request; urllib.request.urlretrieve('https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py', '/tmp/get-poetry.py')" && \
    python /tmp/get-poetry.py -y && \
        rm /tmp/get-poetry.py && \
            /root/.poetry/bin/poetry install --no-dev --no-ansi --no-interaction && \
                rm -rf /root/.poetry

WORKDIR /app

# ここでソースコードのコピー
copy main.py ./
copy gql_compiler ./gql_compiler

USER app

ENTRYPOINT ["python", "main.py"]
