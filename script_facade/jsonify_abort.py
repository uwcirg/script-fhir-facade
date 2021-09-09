"""Utility function to generate JSON response with error (status_code)"""
from flask import jsonify, make_response


def jsonify_abort(status_code, **kwargs):
    """Given kwards included in JSON response using given status_code

    NB - must return from view
    """
    response = make_response(jsonify(kwargs))
    response.status_code = status_code
    return response
