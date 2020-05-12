from fiches_urgence.models import City
from fiches_urgence import db
from config_test import TestApi, client
from nose.tools import eq_, ok_

#    ___ ___ _______   __
#   / __|_ _|_   _\ \ / /
#  | (__ | |  | |  \ V /
#   \___|___| |_|   |_|


CITY = {
    "name": "Hamburg",
    "postalCode": "99999"
}


class TestCity(TestApi):

    # ---------------- GET ----------------
    def test_get_cities(self):
        res = client.get('/cities')
        eq_(200, res.status_code)
        eq_([], res.json)

    def test_get_unknwon(self):
        res = client.get('/cities/unknown')
        eq_(404, res.status_code)

    def test_get_city_id(self):
        res = client.post('/cities', json=CITY)
        CITY["id"] = res.json["id"]

        res = client.get(f'/cities/{CITY["id"]}')
        eq_(200, res.status_code)
        eq_(CITY, res.json)

    # ---------------- POST ----------------
    def test_post_cities_no_data(self):
        res = client.post('/cities')
        eq_(400, res.status_code)

    def test_post_cities(self):
        res = client.post('/cities', json=CITY)
        eq_(201, res.status_code)
        CITY["id"] = res.json["id"]
        eq_(CITY, res.json)

    # ---------------- PUT ----------------
    def test_put_city(self):
        res_post = client.post('/cities', json=CITY)
        new_city = {
            "name": "Tokyo",
            "postalCode": "0000123"
        }
        res = client.put(f'/cities/{res_post.json["id"]}', json=new_city)
        new_city["id"] = res_post.json["id"]
        eq_(200, res.status_code)
        eq_(new_city, res.json)

    # ---------------- DELETE ----------------
    def test_delete_city(self):
        res_post = client.post('/cities', json=CITY)
        res = client.delete(f"/cities/{res_post.json['id']}")
        eq_(204, res.status_code)
