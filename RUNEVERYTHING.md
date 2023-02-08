ClassTranscribe consists as a set of docker images. These instructions walk through setting everything to run locally, including the database, all of the backend projects and the frontend too. You will need to install Docker.

M1 Macs are not currently supported.

## Setting up ClassTranscribe

Create a project directory

```sh
mkdir ClassTranscribe
cd ClassTranscribe
```

Checkout the 3 main projects of ClassTranscribe, FrontEnd,WebAPI and pyapi. On Mac/Linux,
```sh
#Choose your preferred way to authenticate and clone the project...
BASE=git@github.com:classtranscribe
BASE=https://github.com/classtranscribe

git clone $BASE/FrontEnd.git
git clone $BASE/WebAPI.git
git clone $BASE/pyapi.git
```
Or in Windows,
```sh
REM Choose your preferred way to authenticate and clone the project...
set BASE=git@github.com:classtranscribe
set BASE=https://github.com/classtranscribe

git clone %BASE%/FrontEnd.git
git clone %BASE%/WebAPI.git
git clone %BASE%/pyapi.git
```

Unzip the docker compose files (docker-compose.yml and docker-compose.override.yml) and initial environment files (.env). 
Windows Explorer can also be used to unzip the file.
These files are provided as a zip file because you will probably want to edit them.

```sh
cd pyapi
unzip devdocker.zip
```
Change into the devdocker directory 
```
cd devdocker
ls
```

and review these files. For example the .env file sets the port for the frontend
```txt
TRAEFIK_HTTP_PORT=80
TRAEFIK_HTTPS_PORT=443
```

Pull the pre-made docker images from docker hub.
```sh
# You must be in the devdocker directory with the docker-compose files etc.
docker compose pull
```
To save time you can use the premade images for api, frontend and pyapi already on dockerhub.
To also build these projects uncomment the build lines in docker-compose.override.yml
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
