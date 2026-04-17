set dotenv-load
export PYTHONPATH := "./src"

# run dev server localy
[working-directory: 'src']
run:
    uv run uvicorn app.main:create_app --reload --host 0.0.0.0 --port 8000


# create migrations
[working-directory: 'src']
makemigrations MESSAGE="no message":
    uv run alembic revision --autogenerate -m "{{MESSAGE}}"

# apply migrations
[working-directory: 'src']
applymigrations:
    uv run alembic upgrade head


# run tests
[working-directory: '.']
test args="":
    uv run pytest -v -x {{args}}


# Build Docker image
[working-directory: 'deploy']
[group('docker')]
build:
    docker compose build


# Run Docker container
[working-directory: 'deploy']
[group('docker')]
ups:
    docker compose up


[working-directory: 'deploy']
[group('docker')]
up:
    docker compose up -d


# Build and run tests in container
[working-directory: 'deploy']
[group('docker')]
testd:
    #docker compose -f compose-testing.yml up --abort-on-container-exit
    docker compose -f compose-testing.yml up --build --abort-on-container-exit


# Build test image only
[working-directory: 'deploy']
[group('docker')]
buildtestd:
    docker compose -f compose-testing.yml build


# Stop containers
[working-directory: 'deploy']
[group('docker')]
down:
    docker compose down


# Make migrations with docker
[working-directory: 'deploy']
[group('docker')]
applymigrationsd:
    docker compose exec app alembic upgrade head


# Apply migration with docker
[working-directory: 'deploy']
[group('docker')]
makemigrationsd MESSAGE="no message":
    docker compose exec app alembic revision --autogenerate -m '{{MESSAGE}}'


# Show container logs
[working-directory: 'deploy']
[group('docker')]
logsd:
    docker compose logs -f --tail 100