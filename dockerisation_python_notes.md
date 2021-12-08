# Notes on how to dockerise an application

- for python, use this tutorial:
https://docs.docker.com/language/python/build-images/

freeze python dependencies:
(checker plus en détails pour avoir une bonne liste cohérente, faire marcher avec le venv?)
pip3 freeze >> requirements.txt
to do it more precisely by packages, use:
pip3 freeze | grep package-name >> requirements.txt

build the image as: 
 docker build --tag docker-image-tag-name . -f name.Dockerfile

publish the ports and run docker image
(-p for publish)
```docker run -d -p [host port]:[container port] <image_name>```

see the images: docker images
see the containers: docker ps (-a for all)
docker rmi (remove image)
docker rm (remove container)

give data through volumes and networks
https://docs.docker.com/storage/volumes/
curl API calls can be used as well
(define an python API open for this with Flask?)

- for handling different containers, use docker-compose
https://docs.docker.com/compose/



note: create HTTP API servers with Flask to handle the requests and responses

