ClassTranscribe consists as a set of docker images. These instructions walk through setting everything to run locally, including the database, all of the backend projects and the frontend too. 

## Set up Docker correctly!

You will need to install Docker by following the official Docker [instructions](https://docs.docker.com/engine/install/)

Did you install Ubuntu's snap version of Docker? The overlay filesystem won't work! (You might see `Permission denied:` filesystem errors when building from a Dockerfile). So Purge the snap, ```sudo snap remove --purge Docker``` and follow the official Docker install instructions instead.

If you have enough ram, we recommend 6 GB RAM for your Docker Machine.

M1 Macs are not natively supported but can build and run AMD64 images.

## Setting up ClassTranscribe

Create a project directory

```sh
mkdir ClassTranscribe
cd ClassTranscribe
```

Checkout the 3 main projects of ClassTranscribe, FrontEnd,WebAPI and pyapi
```sh
#Choose your prefered way to clone the project...
BASE=git@github.com:classtranscribe
BASE=https://github.com/classtranscribe/

git clone $BASE/FrontEnd.git
git clone $BASE/WebAPI.git
git clone $BASE/pyapi.git
```

Unzip the docker compose files (docker-compose.yml and docker-compose.override.yml) and initial environment files (.env). 
Windows Explorer can also be used to unzip the file.
These files are provided as a zip file because you will probably want to edit them.

```sh
cd pyapi
unzip devdocker.zip
```
Change into the devdocker directory and review these files. For example the .env file sets the port for the frontend
```txt
TRAEFIK_HTTP_PORT=80
TRAEFIK_HTTPS_PORT=443
```

Pull the pre-made docker images from docker hub
```sh
docker compose pull
```
To save time you can use the premade images for api, frontend and pyapi projects already on dockerhub.
Look at docker-compose.override.yml ; if you want to use the pre-made images comment the build lines

```yml
    #build:
    #  context: ../WebAPI
    #  dockerfile: ./pythonrpcserver.Dockerfile
```

Build the project(s). This will take more than 10 minutes, especially the first time.
```sh
docker compose build
```

Start the Postgres database and message queue containers
```sh
docker compose up -d db rabbitmq
```
Just start everything
```sh
docker compose up -d
```
Look at the logs of one or all containers
```sh
# Check the status of all of the containers
docker compose ps
# Look at the last 4 lines of pyapi
docker compose logs --tail=4 pyapi
# Or all containers
docker compose logs --tail=4
# Or follow the output with a timestamp
docker compose logs -tf --tail=4
```
