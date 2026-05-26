FROM python:3.10-slim
# FROM python:3.10

# set work directory
WORKDIR /backend

# set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
COPY req.txt .

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2


RUN pip install -r req.txt

# copy project
COPY . /backend
RUN chmod +x /backend/docker-entrypoint.sh
EXPOSE 8000

CMD ["/backend/docker-entrypoint.sh"]
