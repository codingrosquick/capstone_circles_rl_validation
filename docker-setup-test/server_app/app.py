from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, Docker!'


@app.route('/test')
def hello_world_test():
    return 'Hello, testing Docker!'