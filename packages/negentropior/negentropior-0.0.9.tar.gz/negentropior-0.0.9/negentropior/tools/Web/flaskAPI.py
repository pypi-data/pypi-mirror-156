

from flask import Flask

app = Flask(__name__)


@app.route('/AlgorithmApi', method=['post'])
def post():

    def _in_func(function):
        return function()

    return _in_func


def run(host: str, port: int) -> any:
    app.run(debug=False, host=host, port=port)
