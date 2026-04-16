set dotenv-load
export PYTHONPATH := "./src"

# run dev server localy
[working-directory: 'src']
run:
    uv run uvicorn app.main:create_app --reload --host 0.0.0.0 --port 8000


# create migrations
[working-directory: 'src']
mig-create message:
    uv run alembic revision --autogenerate -m "{{message}}"

# apply migrations
[working-directory: 'src']
mig-apply:
    uv run alembic upgrade head


# run tests
[working-directory: '.']
test args="":
    uv run pytest -s -v -x {{args}}
