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
# On windows use Windows Explore to extract the files of devdocker.zip into a 'devdocker' directory
unzip devdocker.zip
```
Change into the devdocker directory and you should see the 3 files
```
cd devdocker
ls -a
```

Open and review these 3 files (they are just text files) e.g. If you have VS Studio installed, use `code .` will open the current directory.

When you open the .env file you will see it sets the port for the frontend
```txt
TRAEFIK_HTTP_PORT=80
TRAEFIK_HTTPS_PORT=443
```
When you open the docker-compose and docker-compose.override files you will see they are text files contain configuration information for the various docker containers. The override file contains additional settings for the same containers. It's a smaller file so is usually easier to edit.
The full spec for docker compose files is on [docker.com]](https://docs.docker.com/compose/compose-file/compose-file-v3/)

Docker compose has several sub commands,
```sh
docker compoose
```

Let's pull the pre-made docker images from docker hub. This command will use the docker-compose files in the current directory. If it fails you are not in the correct directory.
```sh
# You must be in the devdocker directory with the docker-compose files etc.
docker compose pull
```
To save time you can immediately use the premade images for api, frontend and pyapi already on dockerhub.
To also build these projects from source uncomment the build lines in docker-compose.override.yml, but don't do this immediately.
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
