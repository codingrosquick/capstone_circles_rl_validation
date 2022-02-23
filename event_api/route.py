from flask import Flask
app = Flask(__name__)

# use a POST
@app.route('/config')
def hello_world():
    return 'Hello, Docker!'

# use a GET
@app.route('/next')
def hello_world():
    return 'Hello, Docker!'