from flask import Flask, Response, request
from optimizers.initial_optimizer import main as initial_optimizer
from optimizers.optmizer import main as optimize_team, current_team
from optimizers.repository import Repository
import json, logging
app = Flask(__name__)

ERROR_RESPONSE_BODY = {'message': 'cannot optimize!'}

@app.route("/")
def index():
    return 'Hello world!'

@app.route("/init")
def init():
    return initial_optimizer()

@app.route("/current")
def current():
    try:
        req = request.args
        team_id = req.get("team")
        event = req.get("event")
        return current_team(team_id, event)
    except:
        return ERROR_RESPONSE_BODY, 500

@app.route("/optimize")
def optimize():
    try:
        req = request.args
        team_id = req.get("team")
        event = req.get("event")
        replacement = req.get("replacement") if req.get("replacement") else 1
        return optimize_team(team_id, event, int(replacement))
    except Exception as e:
        logging.error(e)
        return ERROR_RESPONSE_BODY, 500

@app.route("/event")
def event():
    try:
        return Repository().read_current_next_event().to_dict(orient='records')[0]
    except Exception as e:
        logging.error(e)
        return ERROR_RESPONSE_BODY, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5555, debug=True)