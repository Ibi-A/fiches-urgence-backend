from backend.models import Person, Resident
from backend import db
from config_test import TestApi, client, is_dict_subset_of_superset
from nose.tools import eq_, ok_

#   ____  _____ ____ ___ ____  _____ _   _ _____
#  |  _ \| ____/ ___|_ _|  _ \| ____| \ | |_   _|
#  | |_) |  _| \___ \| || | | |  _| |  \| | | |
#  |  _ <| |___ ___) | || |_| | |___| |\  | | |
#  |_| \_\_____|____/___|____/|_____|_| \_| |_|


PERSON = {
    "firstName": "name",
    "lastName": "name",
    "address": "address",
    'alternativePhoneNumber': "altPhone",
    'mainPhoneNumber': "mainPhone"
}

RESIDENT = {
    'birthplace': "birthplace",
    'psychiatrist_id': None,
    'cityId': None,
    'emergencyBag': None,
    'referringDoctorId': None,
    'healthMutualId': None,
    'birthDate': None,
    'entranceDate': None,
    'socialWelfareNumber': None,
}


class TestPerson(TestApi):

    def test_get_residents(self):
        res = client.get('/residents')
        eq_(200, res.status_code)
        eq_([], res.json)

    def test_get_unknwon(self):
        res = client.get('/residents/unknown')
        eq_(404, res.status_code)

    def test_post_residents_no_data(self):
        res = client.post('/residents')
        eq_(400, res.status_code)

    def test_post_residents_unknown_id(self):
        res = client.post('/residents', json={"id": "unknown"})
        eq_(400, res.status_code)

    def test_post_residents(self):
        res_person = client.post('/persons', json=PERSON)
        RESIDENT["id"] = PERSON["id"] = res_person.json["id"]

        res = client.post('/residents', json=RESIDENT)
        eq_(201, res.status_code)

        RESIDENT["person"] = PERSON

        res = client.get(f'/residents/{PERSON["id"]}')
        eq_(200, res.status_code)
        eq_(True, is_dict_subset_of_superset(res.json, RESIDENT))
    # def test_put_person(self):
    #     res_post = client.post('/persons', json=PERSON)
    #     new_person = {
    #         "firstName": "name2",
    #         "lastName": "name2",
    #         "address": "address2",
    #         'alternativePhoneNumber': "altPhone2",
    #         'mainPhoneNumber': "mainPhone2"
    #     }
    #     res = client.put(f'/persons/{res_post.json["id"]}', json=new_person)
    #     new_person["id"] = res_post.json["id"]
    #     eq_(200, res.status_code)
    #     eq_(new_person, res.json)

    # def test_delete_person(self):
    #     res_post = client.post('/persons', json=PERSON)
    #     res = client.delete(f"/persons/{res_post.json['id']}")
    #     eq_(204, res.status_code)
