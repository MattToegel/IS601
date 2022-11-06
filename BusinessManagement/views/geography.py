import pycountry
import json
from flask import Blueprint, request

geo = Blueprint("geo", __name__, url_prefix='/geo')
# TODO DO NOT EDIT
# these are javascript endpoints used from country_state_selector.html
@geo.route("/countries")
def countries():
    # extract just the data we need for our <select> options
    countries = map(lambda c: {"code": c.alpha_2, "name": c.name},list(pycountry.countries))
    return json.dumps(list(countries))

@geo.route("/states")
def states():
    # extract just the data we need for our <select> options
    status = list(map(lambda s: {"name": s.name, "code": s.code.split("-")[1]}, 
        list(pycountry.subdivisions.get(country_code=request.args.get('country_code', 'US')))))
    return json.dumps(status)
