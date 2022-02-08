# Generate SQLAlchemy models from existing DB
Prerequisites:
* A running ClassTranscribe PostgreSQL Database
* Docker and or Python/pip

Run a Docker container with Python 3 (if necessary):
```bash
$ docker run --net=host -it --rm -v $(pwd):/usr/app -w /usr/app python:3 bash
```

Wherever `pip` and `python` are available, install sqlacodegen and the psycopg2 pre-built binary:
```bash
% pip install psycopg2_binary sqlacodegen==3.0.0b2   # Needed to support SQLA > v1.3
```
NOTE: this specific (beta) version is currently needed to work with SQLAlchemy

The `psycopg2` tool allows us to connect to postgres, and the `sqlacodegen` utility will translate your existing 
PostgreSQL database tables into usable SQLAlchemy models:
```bash
% sqlacodegen postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@localhost:5432/ct2019db --outfile ./entities.py
```