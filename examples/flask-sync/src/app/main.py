import os

from flask import Flask, send_from_directory, jsonify
from flask.views import MethodView

from app.business.table_defs import DatabaseGateway
from microapi.extension import specification_from_endpoints

# --- Setup database ---
DatabaseGateway.create(
    "sqlite://"
)
db_gateway = DatabaseGateway.instance()


# --- Application factory ---
def create_app(named_endpoints):
    application = Flask(__name__,
                        static_url_path="/docs",
                        static_folder=os.path.abspath("openapi-statics")
                        )
    endpoints = list(endpoint for name, endpoint in named_endpoints)
    for name, endpoint in named_endpoints:
        application.add_url_rule(endpoint.route(), view_func=endpoint.as_view(name))

    class OpenAPiView(MethodView):
        _SPECIFICATION_ = specification_from_endpoints(endpoints)
        def get(self):
            return jsonify(self._SPECIFICATION_.to_dict())


    application.add_url_rule("/openapi.json", view_func=OpenAPiView.as_view('openapi_documentation'))
    return application


# --- Create HTTP views, and attach them in the application (routing) ---
from app.endpoints.greeting import GreetingDetail
from app.endpoints.greeting_repository import Greeting

endpoints = [
    ('greeting_page', Greeting),
    ('greeting_entity', GreetingDetail)
]

appserver = create_app(endpoints)


@appserver.route('/docs/<path:path>')
def send_report(path):
    return send_from_directory('openapi-statics', path)

