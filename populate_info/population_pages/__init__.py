from flask import Blueprint

item_blueprint = Blueprint("add", __name__)

from populate_info.population_pages import breaking_population, start_population
