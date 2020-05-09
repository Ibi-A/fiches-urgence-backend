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

# #   _____ ___ ___ _____ ___
# #  |_   _| __/ __|_   _/ __|
# #    | | | _|\__ \ | | \__ \
# #    |_| |___|___/ |_| |___/

#     def test_index_page_successful(self):
#         """
#         Every single test in this test group should be defined as a method of this class.

#         The methods should be named as follows: test_<name_of_test>
#         """

#         with self.client:
#             response = self.client.get('/')
#             self.assertEqual(response.status_code, 404)

#     def test_something2(self):

#         user = Person(
#             id="id",
#             firstName="hello",
#             lastName="pls",
#             address="ad"
#         )
#         db.session.add(user)
#         db.session.commit()
#         # this works
#         response = self.client.get("/persons").json
#         assert len(response) == 1

#     def test_post_persons():
#         person = {
#             "firstName": "name",
#             "lastName": "name",
#             "address": "address",
#             'alternativePhoneNumber': "altPhone",
#             'mainPhoneNumber': "mainPhone"
#         }
#         res = client.post('/persons', json=person)

#         eq_(201, res.status_code)
#         person["id"] = res.json["id"]

#         res = client.get(f'/persons/{person["id"]}')
#         eq_(200, res.status_code)
#         eq_(person, res.json)

#     def test_post_persons(self):
#         person = {
#             "firstName": "name",
#             "lastName": "name",
#             "address": "address",
#             'alternativePhoneNumber': "altPhone",
#             'mainPhoneNumber': "mainPhone"
#         }
#         res = client.post('/persons', json=person)

#         res = client.get(f'/persons')


# from unittest import TestCase
# from nose.tools import eq_, ok_
# from backend import create_app

# app = create_app()
# app.testing = True
# client = app.test_client()


# class TestUtils(TestCase):

#     def setUp(self):
#         db.create_all()

#     def tearDown(self):
#         db.session.remove()
#         db.drop_all()

#     def test_get_persons():
#         res = client.get('/persons')
#         eq_(200, res.status_code)

#     def test_post_persons_no_data():
#         res = client.post('/persons')
#         eq_(400, res.status_code)

#     def test_post_persons():
#         person = {
#             "firstName": "name",
#             "lastName": "name",
#             "address": "address",
#             'alternativePhoneNumber': "altPhone",
#             'mainPhoneNumber': "mainPhone"
#         }
#         res = client.post('/persons', json=person)

#         eq_(201, res.status_code)
#         person["id"] = res.json["id"]

#         res = client.get(f'/persons/{person["id"]}')
#         eq_(200, res.status_code)
#         eq_(person, res.json)

#     def test_post_persons():
#         person = {
#             "firstName": "name",
#             "lastName": "name",
#             "address": "address",
#             'alternativePhoneNumber': "altPhone",
#             'mainPhoneNumber': "mainPhone"
#         }
#         res = client.post('/persons', json=person)

#         res = client.get(f'/persons')
#         print(res.json)
#         eq_(1, 2)
