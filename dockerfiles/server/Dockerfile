FROM python:3.9-slim-buster

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  GIT_PYTHON_REFRESH=quiet

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN python3 manage.py collectstatic --no-input