# ClassTranscribe Python API

Powered by Flask + Connexion + SQLAlchemy


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

