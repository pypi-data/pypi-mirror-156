
from flask import Flask
from nova_server.route.train import train
from nova_server.route.predict import predict
from nova_server.route.status import status
from nova_server.route.ui import ui
from nova_server.tests.test_route import test


def create_app():
    print("Starting nova-backend server")
    app = Flask(__name__)
    app.register_blueprint(train)
    app.register_blueprint(predict)
    app.register_blueprint(status)
    app.register_blueprint(ui)
    app.register_blueprint(test)
    return app

if __name__ == "__main__":
    from waitress import serve

    app = create_app()
    serve(app, host="127.0.0.1", port=8080)


# TODO: Init database access
# app.config['MONGODB_SETTINGS'] = {
# 'host': 'mongodb://localhost/movie-bag'
# }
