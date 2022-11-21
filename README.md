# ClassTranscribe Python API

Powered by Flask + Connexion + SQLAlchemy

## Build Status

| Branch | Status |
|-------:|--------|
| Production | ![Production](https://github.com/classtranscribe/pyapi/actions/workflows/docker.yml/badge.svg?event=push&branch=main) |
| Staging | ![Staging](https://github.com/classtranscribe/pyapi/actions/workflows/docker.yml/badge.svg?event=push&branch=staging) |
| Experiment | ![Experiment](https://github.com/classtranscribe/pyapi/actions/workflows/docker.yml/badge.svg?event=push&branch=expt) |
​
## Configuration
Environment variables can be used to set the configuration.

### Application Config
| Environment Variable    | Description | Default Value |
| ------ | ----------- | ----- |
| DEBUG | Enable verbose debug output | `False` |
| PORT | The port to serve the Flask app | 5000 |
| SWAGGER_URL | local or remote URL to the Swagger spec that this application uses | `openapi/swagger.json` |

### Database Connection Config
You can choose to connect to a remote postgres instance, or use a local SQLite file (recommended for dev only)

| Environment Variable    | Description | Default Value |
| ------ | ----------- | ----- |
| USE_SQLITE | Use a local database file (instead of postgres, for local dev only) | True |
| POSTGRES_HOST | Hostname of a remote Postgres to connect to | `localhost` |
| POSTGRES_PORT | Port of a remote Postgres to connect to | 5432 |
| POSTGRES_USER | Username to use when connecting to remote Postgres | '' |
| POSTGRES_PASS | Password to use when connecting to remote Postgres | '' |
| POSTGRES_DB | Database to use when connecting to remote Postgres | `ct2019db` |

NOTE: By default, a sqlite file will be created.

## Getting Started
This project can either be run with Python or as a Docker container.

### With Python
Install dependencies:
```bash
pip install -r requirements.txt
```

Run the application:
```bash
python server.py
```

Navigate to http://localhost:5000/ui/ to test the API with Swagger UI.

### With Docker
Build the Docker image:
```bash
docker build -t classtranscribe/pyapi .
```

Run a Docker container from that image:
```bash
docker run -itd --name ct-pyapi -p 5000:5000 classtranscribe/pyapi
```

Navigate to http://localhost:5000/ui/ to test the API with Swagger UI.

NOTE: In Docker on Mac/Windows, you may need to use your IP address instead of localhost.

### With Docker Compose
Build and run the pyapi application, along with `postgres` and `rabbitmq`:
```bash
docker compose -f docker/docker-compose.yml up -d --build
```

You can change the code and/or `.env` files located in the Docker directory to change the behavior of the application.

NOTE: `--build` will automatically rebuild the Docker image needed for this stack

Navigate to http://localhost:5000/ui/ to test the API with Swagger UI.

NOTE: In Docker on Mac/Windows, you may need to use your IP address instead of localhost.


## TODO
* Produce schemas/repositories for generated models
* Test generated models with basic example
* RabbitMQ connections
* Parity for WebAPI behavior
* Parity for TaskEngine subproject