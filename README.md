# Micro-OpenAPI

## Install

First install the `microapi` library in a fresh environment.
```py
python3.9 -m venv venv39
source venv39/bin/activate
pip install -r requirements.txt
pip install mypy
pip install build

# Run MyPy, for satisfaction purpose

python -m build

# Install the wheel in your environment
```

## Run the examples

### Flask

Carefully follows the instructions below.

First, install the specific requirements.
Next, run a GUnicorn server:
```
gunicorn --reload --bind localhost:8000 app.main:appserver
```
Curl it:
```
curl -v localhost:8000/greeting
```
If it doesn't work, that is bad.

Upon success, curl the `/openapi.json` end-point
and observe the result in Swagger Editor online. Alternatively, you can also
set-up a static file service.