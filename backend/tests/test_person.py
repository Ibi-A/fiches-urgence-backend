from backend.models import Person
from backend import db
from config_test import TestWebsite, client
from nose.tools import eq_, ok_

#   ___ ___ ___  ___  ___  _  _
#  | _ \ __| _ \/ __|/ _ \| \| |
#  |  _/ _||   /\__ \ (_) | .` |
#  |_| |___|_|_\|___/\___/|_|\_|


class TestPerson(TestWebsite):

    def test_get_persons(self):
        res = client.get('/persons')
        eq_(200, res.status_code)

    def test_post_persons_no_data(self):
        res = client.post('/persons')
        eq_(400, res.status_code)

    def test_post_persons(self):
        person = {
            "firstName": "name",
            "lastName": "name",
            "address": "address",
            'alternativePhoneNumber': "altPhone",
            'mainPhoneNumber': "mainPhone"
        }
        res = client.post('/persons', json=person)

        eq_(201, res.status_code)
        person["id"] = res.json["id"]

        res = client.get(f'/persons/{person["id"]}')
        eq_(200, res.status_code)
        eq_(person, res.json)

    def test_post_persons(self):
        person = {
            "firstName": "name",
            "lastName": "name",
            "address": "address",
            'alternativePhoneNumber': "altPhone",
            'mainPhoneNumber': "mainPhone"
        }
        res = client.post('/persons', json=person)

        res = client.get(f'/persons')
        ok_(res.json)
        ok_
