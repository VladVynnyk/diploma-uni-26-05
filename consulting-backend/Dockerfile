FROM python:3.10-slim
# FROM python:3.10

# set work directory
WORKDIR /backend

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
COPY consulting-backend/req.txt .

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2


RUN pip install -r req.txt

# copy project
COPY consulting-backend /backend
RUN mkdir -p /backend/deployment/generated
COPY deployment/avatar_manifest.json /backend/deployment/avatar_manifest.json
RUN chmod +x /backend/docker-entrypoint.sh
EXPOSE 8000

CMD ["/backend/docker-entrypoint.sh"]
