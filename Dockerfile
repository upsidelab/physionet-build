FROM python:3.9

RUN apt-get update -y \
    && apt-get upgrade -y \
    && apt-get install postgresql-client zip -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY . /code
RUN chmod +x /code/wait-for-it.sh
WORKDIR /code

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-root