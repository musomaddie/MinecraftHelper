from flask import Blueprint

item_blueprint = Blueprint("add", __name__)

from populate_info.population_pages import (breaking_population, crafting_population, start_population,
    env_changes_population)
