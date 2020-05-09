from backend import create_app, db
from flask_testing import TestCase
import unittest
import logging
import os
from nose.tools import eq_, ok_

basedir = os.path.abspath(os.path.dirname(__file__))


# Creates a new instance of the Flask application. The reason for this
# is that we can't interrupt the application instance that is currently
# running and serving requests.
app = create_app()
client = app.test_client()


class TestWebsite(TestCase):

    #   _____ ___ ___ _____    ___ ___  _  _ ___ ___ ___
    #  |_   _| __/ __|_   _|  / __/ _ \| \| | __|_ _/ __|
    #    | | | _|\__ \ | |   | (_| (_) | .` | _| | | (_ |
    #    |_| |___|___/ |_|    \___\___/|_|\_|_| |___\___|

    def create_app(self):
        """
        Instructs Flask to run these commands when we request this group of tests to be run.
        """

        # Sets the configuration of the application to 'TestingConfig' in order
        # that the tests use db_test, not db_dev or db_prod.
        # app.config.from_object('config_test.Config')
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
            'sqlite:///' + os.path.join(basedir, 'db_instances', 'test.db')
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        # Sets the logger to only show ERROR level logs and worse. We don't want
        # to print a million things when running tests.
        return app

    def setUp(self):
        """Defines what should be done before every single test in this test group."""
        db.create_all()

    def tearDown(self):
        """Defines what should be done after every single test in this test group."""
        db.session.remove()
        db.drop_all()