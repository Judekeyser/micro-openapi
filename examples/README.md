# Run the examples

In order to run the example, make sure you have installed the library in an environment
(or globally on your Python install, if you believe in Destiny);
See [install instructions](../README.md).

## Flask

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