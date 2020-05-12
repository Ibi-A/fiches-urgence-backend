from fiches_urgence.models import Contributor
from fiches_urgence import db
from nose.tools import eq_, ok_
from config_test import TestApi, client, is_dict_subset_of_superset


#    ___ ___  _  _ _____ ___ ___ ___ _   _ _____ ___  ___
#   / __/ _ \| \| |_   _| _ \_ _| _ ) | | |_   _/ _ \| _ \
#  | (_| (_) | .` | | | |   /| || _ \ |_| | | || (_) |   /
#   \___\___/|_|\_| |_| |_|_\___|___/\___/  |_| \___/|_|_\


PERSON = {
    "firstName": "name",
    "lastName": "name",
    "address": "address",
    'alternativePhoneNumber': "altPhone",
    'mainPhoneNumber': "mainPhone"
}

CONTRIBUTOR = {
    "role": "contributor"
}


class TestContributor(TestApi):

    def setUp(self):
        """ Overloads setUp method to automatically create a new Person """
        super(TestContributor, self).setUp()
        res_person = client.post('/persons', json=PERSON)
        CONTRIBUTOR["id"] = PERSON["id"] = res_person.json["id"]

    # ---------------- GET ----------------
    def test_get_contributors(self):
        res = client.get('/contributors')
        eq_(200, res.status_code)
        eq_([], res.json)

    def test_get_unknwon(self):
        res = client.get('/contributors/unknown')
        eq_(404, res.status_code)

    def test_get_contributor_id(self):
        res = client.post('/contributors', json=CONTRIBUTOR)
        eq_(201, res.status_code)

        res = client.get(f'/contributors/{CONTRIBUTOR["id"]}')
        eq_(200, res.status_code)
        eq_(True, is_dict_subset_of_superset(CONTRIBUTOR, res.json))

    # ---------------- POST ----------------
    def test_post_contributors_no_data(self):
        res = client.post('/contributors')
        eq_(400, res.status_code)

    def test_post_contributors_unknown_id(self):
        res = client.post('/contributors', json={"id": "unknown"})
        eq_(400, res.status_code)

    def test_post_contributors(self):
        res = client.post('/contributors', json=CONTRIBUTOR)
        eq_(201, res.status_code)
        ok_(res.json["id"])
        eq_(True, is_dict_subset_of_superset(CONTRIBUTOR, res.json))

    # ---------------- PUT ----------------
    def test_put_contributor(self):
        res_post = client.post('/contributors', json=CONTRIBUTOR)

        new_contributor = {
            "role": "otherRole"
        }
        res = client.put(
            f'/contributors/{ CONTRIBUTOR["id"]}', json=new_contributor)
        new_contributor["id"] = CONTRIBUTOR["id"]

        eq_(200, res.status_code)
        eq_(True, is_dict_subset_of_superset(new_contributor, res.json))

    # ---------------- DELETE ----------------
    def test_delete_contributo(self):
        res_post = client.post('/contributors', json=CONTRIBUTOR)

        res = client.delete(f"/contributors/{res_post.json['id']}")
        eq_(204, res.status_code)