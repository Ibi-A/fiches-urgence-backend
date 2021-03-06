from config_test import TestApi, client
from nose.tools import eq_

#   ___ ___ ___  ___  ___  _  _
#  | _ \ __| _ \/ __|/ _ \| \| |
#  |  _/ _||   /\__ \ (_) | .` |
#  |_| |___|_|_\|___/\___/|_|\_|


PERSON = {
    "firstName": "name",
    "lastName": "name",
    "address": "address",
    'alternativePhoneNumber': "altPhone",
    'mainPhoneNumber': "mainPhone"
}


class TestPerson(TestApi):

    # ---------------- GET ----------------
    def test_get_persons(self):
        res = client.get('/persons')
        eq_(200, res.status_code)
        eq_([], res.json)

    def test_get_unknwon(self):
        res = client.get('/persons/unknown')
        eq_(404, res.status_code)

    def test_get_person_id(self):
        res = client.post('/persons', json=PERSON)
        PERSON["id"] = res.json["id"]
        res = client.get(f'/persons/{PERSON["id"]}')
        eq_(200, res.status_code)
        eq_(PERSON, res.json)

    # ---------------- POST ----------------
    def test_post_persons_no_data(self):
        res = client.post('/persons')
        eq_(400, res.status_code)

    def test_post_persons(self):
        res = client.post('/persons', json=PERSON)
        eq_(201, res.status_code)

        PERSON["id"] = res.json["id"]
        eq_(PERSON, res.json)

    # ---------------- PUT ----------------
    def test_put_person(self):
        res_post = client.post('/persons', json=PERSON)
        new_person = {
            "firstName": "name2",
            "lastName": "name2",
            "address": "address2",
            'alternativePhoneNumber': "altPhone2",
            'mainPhoneNumber': "mainPhone2"
        }
        res = client.put(f'/persons/{res_post.json["id"]}', json=new_person)
        new_person["id"] = res_post.json["id"]
        eq_(200, res.status_code)
        eq_(new_person, res.json)

    # ---------------- DELETE ----------------
    def test_delete_person(self):
        res_post = client.post('/persons', json=PERSON)
        res = client.delete(f"/persons/{res_post.json['id']}")
        eq_(204, res.status_code)
