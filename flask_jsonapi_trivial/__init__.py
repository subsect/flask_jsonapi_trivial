"""
    Provides Flask with *very basic* compliance with JSONAPI.org enabling easy
    construction of APIs that return JSON.

    Exceptions raised by the following modules are automatically transformed
    to JSONAPI while keeping the correct HTTP headers:

    - Jose JWT
    - Werkzeug (for Flask itself)
"""

import jose.exceptions
import inspect
import json
import logging
import werkzeug.exceptions

from flask import Response
from functools import wraps
from http import HTTPStatus
from uuid import uuid4

_jsonapi_version = "1.0"


def jsonapi(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        obj = werkzeug.exceptions.InternalServerError
        data = {}
        included = None
        links = None
        meta = None

        _json = {}

        r = f(*args,**kwargs)

        try:
            obj,_json = r
        except (ValueError):
            # r is not a tuple.
            obj = r
            _json = {}
        except (TypeError):
            # r is not a tuple, and is probably (hopefully) an HTTPStatus or
            # werkzeug.exceptions object.
            obj = r
            _json = {}

        if "data" in _json: data = _json["data"]
        if "included" in _json: included = _json["included"]
        if "links" in _json: links = _json["links"]
        if "meta" in _json: meta = _json["meta"]

        return jsonapi_response(obj,data=data,included=included,links=links,meta=meta)

    return decorated



def jsonapi_response(obj=werkzeug.exceptions.InternalServerError,
                     data={},
                     included=None,
                     meta=None,
                     links=None,
                     mimetype="application/vnd.api+json",
                     type_=None,
                     indent=2,
                     jsonapi_version=_jsonapi_version,
                     show_version=True,
                     separators=(",",": ")
):
    """
    A simple function to return HTTP responses in a fairly consistent format
    compliant with JSONAPI.org. Use this function instead of the standard
    Flask Response(). In fact, this function does return a Flask Response()
    but in a consistent manner so API users can predict its behaviour.
    """

    message = werkzeug.exceptions.InternalServerError.description
    status_code = werkzeug.exceptions.InternalServerError.code

    # Find out what sort of object might have been passed, and determine
    # a status code to deliver. Uses string comparison (yuck) but the strings
    # are from the objects and modules themselves so should be reliable.

    if type(obj) is dict:
        data = [ obj ]
        status_code = HTTPStatus.OK
        message = None

    if obj != werkzeug.exceptions.InternalServerError:
        if inspect.getmodule(obj):
            n = inspect.getmodule(obj).__name__
            if n == inspect.getmodule(werkzeug.exceptions).__name__:
                message = obj.description
                status_code = obj.code
            elif n == inspect.getmodule(jose.exceptions).__name__:
                message = werkzeug.exceptions.Unauthorized.description
                status_code = werkzeug.exceptions.Unauthorized.code
                if meta is None: meta = {}
                meta["JWT error"] = str(obj)
            elif n == inspect.getmodule(HTTPStatus).__name__:
                message = obj.description
                status_code = obj.value
        elif type(obj) == str:
            data = [{
                "id": str(uuid4().int),
                "jsonapi": {
                    "version": str(jsonapi_version)
                },
                "attributes": {"body": obj},
                "type": type_
            }]
            if not show_version:
                data[0].pop("jsonapi")
            status_code = HTTPStatus.OK

    # In case of 4xx and 5xx errors, abort early:
    if status_code >= 400 and status_code < 600:
        response_object = {}
        error_object = {
            "status": str(status_code),
            "title": message
        }
        if meta:
            error_object["meta"] = meta
        response_object["errors"] = [error_object]
        return Response(
            json.dumps(response_object, indent=indent, separators=separators),
            status=status_code,
            mimetype=mimetype
        )

    response_object = {
        "data": []
    }

    if data is not None:
        if data is not []:
            data = _sanitise(data)
        response_object["data"] = data

    if included is not None:
        included = _sanitise(included)
        response_object["included"] = included

    if meta is not None:
        # meta = _sanitise(meta, add_id=False)
        response_object["meta"] = meta

    if links is not None:
        # links = _sanitise(links, add_id=False)
        response_object["links"] = links

    return Response(
        json.dumps(response_object, indent=indent, separators=separators),
        status=status_code,
        mimetype=mimetype
    )


def _sanitise(o=None,add_id=True):
    """
    Sanity checks to ensure objects are JSONAPI.org compliant. Currently, this
    only performs one check: adds a uuid4 random "id" if there isn't one.
    """
    if add_id and type(o) is dict and not "id" in o:
        o.update({"id":str(uuid4().int)})
    return o


class JsonApiModel(object):
    """
    Subclass this in your models so they return a JSONAPI.org compliant 
    representation. You only need to implement a function called json()
    which needs to return a dict. Note, all values should be strings and
    appropriately formatted to ensure JSONAPI.org compliance.

    The following are special words in JSONAPI.org spec so be careful
    when using them as key/column names in your models:

    - attributes
    - data
    - errors
    - href
    - id (should be okay to use as you normally would)
    - included
    - jsonapi
    - links
    - meta
    - related
    - relationships
    - self
    - type

    The model in the example usage below might produce the following:

    {
      "data": [
        {
          "attributes": {
            "name": "Who Ever",
            "last_seen": "2018-12-23 17:33:14.521342"
          },
          "id": "123",
          "jsonapi": {
            "version": "1.0"
          },
          "type": null
        }
      ]
    }

    Example usage:

    import json
    from datetime import datetime
    from flask_jsonapi_trivial import JsonApiModel
    from flask_sqlalchemy import SQLAlchemy

    db = SQLAlchemy()

    class MyModel(db.Model, JsonApiModel):
        __tablename__ = 'my_table'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String)
        last_seen = db.Column(db.DateTime, default=datetime.utcnow)

        def json(self):
            return {
                "id": str(self.id),
                "name": str(self.name),
                "last_seen": json.loads(json.dumps(self.last_seen,default=str))
            }
    """

    def jsonapi(self):
        """
        Return a JSONAPI.org compliant representation of the model.
        """
        return_object = {
            "attributes": None,
        }

        self_json = self.json()
        tmp_id = self_json.pop("id", None)
        tmp_type = self_json.pop("type", None)

        if tmp_id:
            return_object["id"] = str(tmp_id)
        if tmp_type:
            return_object["type"] = str(tmp_type)

        return_object["attributes"] = self_json

        return return_object


    def jsonapi_limited(self,show_id=False):
        """
        Return a JSONAPI.org compliant representation of the model suitable 
        for public display, i.e. with attributes values removed. Keys are 
        retained.

        This might be useful in an API that should reveal limited info
        when requested by a non-logged in user, but complete info when
        requested by a logged in user.

        Over-ride this function if you want different behaviour.
        """
        return_object = self.jsonapi()

        # FIXME Could recurse into object and nullify all values,
        # leaving all keys..?
        if "id" in return_object and not show_id:
            return_object["id"] = None
        for k in return_object["attributes"]:
            return_object["attributes"][k] = None
        return return_object


    def json(self):
        raise NotImplementedError
