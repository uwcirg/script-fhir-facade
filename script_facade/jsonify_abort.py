"""Utility function to bring together flask `abort` and `jsonify`"""
from flask import abort, jsonify, make_response

def jsonify_abort(**kwargs):
    """Takes any number of args, like jsonify, but raises like abort with correct content_type heading"""
    status_code = kwargs.pop('status_code', 500)
    response = make_response(jsonify(kwargs))
    response.status_code = status_code
    abort(response)
