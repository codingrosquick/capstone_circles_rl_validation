# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster
WORKDIR /app
COPY ./requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY ./app.py .
ENTRYPOINT ["python3"]
CMD ["-m" , "flask", "run", "--host=0.0.0.0"]


# simple python config, from: https://docs.docker.com/language/python/build-images/
# currently stopped at: https://docs.docker.com/language/python/develop/ & volume handling https://docs.docker.com/storage/volumes/

# build this with: docker build --tag python-docker .
# run this with: docker run -d -p 8000:5000 python-docker
# -p: it exposes port 5000 in container to port 8000 out of the container
# -d: detached mode

# docker ps -a, docker images to see

# running a DB: https://docs.docker.com/language/python/develop/
# this is SQL, find how to just handle CSV file locally -> in volumes? or simply in files?
