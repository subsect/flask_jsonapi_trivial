from flask import Flask, abort
from flask_jsonapi_trivial import jsonapi, JsonApiModel
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug import exceptions
import json

db = SQLAlchemy()
app = Flask(__name__)

# Add the @jsonapi decorator and return a
# status or exception, plus optional JSON
# object. Only keys 'meta', 'included',
# 'data', and 'links' are taken from this
# JSON object. Anything else is ignored.
@app.route("/")
@jsonapi
def hello_world():
    return HTTPStatus.OK, { "meta": "Hello, world!" }

# Get Flask to return JSON for exceptions.
# Exceptions raised Werkzeug and Jose
# are supported, as well as all HTTPStatus types.
@app.errorhandler(jose.exceptions.JWTError)
@app.errorhandler(exceptions.NotImplemented)
def custom_error_handler(e):
    return jsonapi_response(e)

# Standard errors can simply be raised, the
# custom error handler catches them.
@app.route('/raise')
def raise_error():
    raise exceptions.NotImplemented

# Errors can simply be returned as well:
@app.route('/show_error')
def show_error():
    return exceptions.ImATeapot


# Flask abort() will return JSON if the error
# handler has been registered, provided it is
# called with an appropriate numerical code.
@app.route('/abort')
def flask_abort():
    abort(exceptions.NotImplemented.code)


# Flask-JSONAPI-trivial allows standard database
# models to easily expose a jsonapi() method
# simply by extending JsonApiModel class.
# The class needs to implement a json()
# method which needs to return a dict JSON
# representation. Appropriate formatting is
# up to you -- see below for an example.
class MyModel(db.Model, JsonApiModel):
    __tablename__ = 'my_table'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self):
        self.id = None
        self.name = "Default Name"
        self.last_seen = datetime.utcnow()

    def json(self):
        if self.id is not None:
            self.id = str(self.id)
        if self.name is not None:
            self.name = str(self.name)
        return {
            "id": self.id,
            "name": self.name,
            "last_seen": json.loads(json.dumps(self.last_seen,default=str))
        }

# Then it's simple to return the JSON representation
# of the model. Correct headers etc are taken care of.
@app.route('/show_model')
def show_model():
    model = MyModel()
    model.id = 1
    model.name = "Whom So Ever"
    return HTTPStatus.OK, model.jsonapi()

# The method jsonapi_limited() strips all detail
# from the model, leaving the keys intact. Any "id"
# field is removed unless specified.
@app.route('/show_limited_model')
def show_limited_model():
    model = MyModel()
    model.id = 999
    model.name = "Limited Model"
    return HTTPStatus.OK, model.jsonapi_limited(show_id=True)