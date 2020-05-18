import os
from flask_testing import TestCase
from fiches_urgence import create_app, db, config

basedir = os.path.abspath(os.path.dirname(__file__))


# Creates a new instance of the Flask application. The reason for this
# is that we can't interrupt the application instance that is currently
# running and serving requests.

class TestApi(TestCase):

    #   _____ ___ ___ _____    ___ ___  _  _ ___ ___ ___
    #  |_   _| __/ __|_   _|  / __/ _ \| \| | __|_ _/ __|
    #    | | | _|\__ \ | |   | (_| (_) | .` | _| | | (_ |
    #    |_| |___|___/ |_|    \___\___/|_|\_|_| |___\___|

    def create_app(self):
        """
        Instructs Flask to run these commands when we request this group of
        tests to be run.
        """
        app = create_app()
        app.config.from_object(config.ConfigTest)
        return app

    def setUp(self):
        """Defines what should be done before every single test"""
        db.create_all()

    def tearDown(self):
        """Defines what should be done after every single test"""
        db.session.remove()
        db.drop_all()


app = TestApi().create_app()
client = app.test_client()


def is_dict_subset_of_superset(subset: dict, superset: dict) -> bool:
    """ Checks if a dictionnary is a subnet of a larger or same of
    another smaller dictionnary

    Args:
        superset (dict): the larger dictionnary
        subset (dict): the smaller dictionnary
    Returns:
        bool: True if the subset is part of the superset, False otherwise
    """
    return subset.items() <= superset.items()
