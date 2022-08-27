from flask import Flask
from optimizers.initial_optimizer import main as initial_optimizer
app = Flask(__name__)

@app.route("/")
def index():
    return 'Hello world!'

@app.route("/init")
def init():
    return initial_optimizer()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)