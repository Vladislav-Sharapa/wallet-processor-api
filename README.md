
The project uses the [Taskfile](https://taskfile.dev/) utility and provides the following commands:
```bash
 * app:start:          "Start fastapi application"
 * docker:down:        "Stop dev docker containers"
 * docker:prod:        "Run application in docker"
 * docker:tests:       "Run test enviroment"
 * docker:up:          "Run dev docker containers"
 * worker:start:       "Start taskiq workers"
```
If you don't use [Taskfile](https://taskfile.dev/) utility, you can just copy commands from the relevant "cmds" items.


## Running the Development Environment
Use the development Docker Compose file with Taskfile commands:
```bash 
# Build and start all services
task docker:up
```
This starts the following services:
 - PostgreSQL – development database
 - RabbitMQ – message broker for TaskIQ
 - MinIO – file storage for reports
 - Redis – caching layer
 - MailDev – email testing (password reset, etc.)

1. After the containers are up for the first time, you need run database migrations (Alembic):
 ```bash
 docker exec -it <app_container_name/id> python -m alembic upgrade head
 ```
2. Start the worker (or use Taskfile):
```bash
task worker:start
```
3. Run the FastAPI application locally (after all Docker services are running):
```bash
python -m app.manage
```
Or use the Taskfile shortcut:
```bash
task app:start
```
## Testing
Run Tests Locally
```bash
python -m pytest -v
```
Run Tests in Docker
```bash
task docker:tests
```
## Production Deployment
To run the application in a container:
```bash
task docker:prod
```
When running the production container for the first time, apply database migrations:
```bash
docker exec -it <app_container_name/id> python -m alembic upgrade head
```