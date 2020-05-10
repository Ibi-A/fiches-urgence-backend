from fiches_urgence.models import Person, Resident
from fiches_urgence import db
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
    'id': None,
    'birthplace': "birthplace",
    'psychiatristId': None,
    'cityId': None,
    'emergencyBag': None,
    'referringDoctorId': None,
    'healthMutualId': None,
    'birthDate': None,
    'entranceDate': None,
    'socialWelfareNumber': None,
}


class TestResident(TestApi):

    def setUp(self):
        """ Overloads setUp method to automatically create a new Person """
        super(TestResident, self).setUp()
        res_person = client.post('/persons', json=PERSON)
        RESIDENT["id"] = PERSON["id"] = res_person.json["id"]

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
        res = client.post('/residents', json=RESIDENT)
        eq_(201, res.status_code)

        RESIDENT["person"] = PERSON

        res = client.get(f'/residents/{RESIDENT["id"]}')
        eq_(200, res.status_code)
        eq_(True, is_dict_subset_of_superset(RESIDENT, res.json))

        # Remove 'person' key and value from RESIDENT not to impact following
        # tests using it
        del RESIDENT["person"]

    def test_delete_resident(self):
        res_post = client.post('/residents', json=RESIDENT)

        res = client.delete(f"/residents/{res_post.json['id']}")
        eq_(204, res.status_code)

    def test_put_resident(self):
        res_post = client.post('/residents', json=RESIDENT)

        new_resident = {
            'birthplace': "birthplace",
            'psychiatristId': None,
            'cityId': None,
            'emergencyBag': None,
            'referringDoctorId': None,
            'healthMutualId': None,
            'birthDate': None,
            'entranceDate': None,
            'socialWelfareNumber': "1234567890",
        }

        res = client.put(f'/residents/{ RESIDENT["id"]}', json=new_resident)
        new_resident["id"] = RESIDENT["id"]
        new_resident["person"] = PERSON
        eq_(200, res.status_code)
        eq_(True, is_dict_subset_of_superset(new_resident, res.json))

    def test_resident_doctor(self):
        # Creates a resident
        res_resident_post = client.post('/residents', json=RESIDENT)

        # Creates a person
        doctor = {
            "firstName": "doctorFirst",
            "lastName": "doctorLast",
            "address": "doctorAddress"
        }
        res_post_doctor = client.post('/persons', json=doctor)

        # Links the person to the resident through the referringDoctorId
        new_resident = {
            'referringDoctorId': res_post_doctor.json["id"],
        }
        res_put = client.put(
            f'/residents/{res_resident_post.json["id"]}', json=new_resident)

        # Check if doctor attribute is created, and with right values
        res = client.get(f'/residents/{RESIDENT["id"]}')
        ok_(res.json["doctor"])
        eq_(res.json["referringDoctorId"], res.json["doctor"]["id"])
        eq_(True, is_dict_subset_of_superset(doctor, res.json["doctor"]))

    def test_resident_psychiatrist(self):
        # Creates a resident
        res_resident_post = client.post('/residents', json=RESIDENT)

        # Creates a person
        psychiatrist = {
            "firstName": "psychiatristFirst",
            "lastName": "psychiatristLast",
            "address": "psychiatristAddress"
        }
        res_post_psychiatrist = client.post('/persons', json=psychiatrist)

        # Links the person to the resident through the referringDoctorId
        new_resident = {
            'psychiatristId': res_post_psychiatrist.json["id"],
        }
        res_put = client.put(
            f'/residents/{res_resident_post.json["id"]}', json=new_resident)

        # Check if psychiatrist attribute is created, and with right values
        res = client.get(f'/residents/{RESIDENT["id"]}')
        ok_(res.json["psychiatrist"])
        eq_(res.json["psychiatristId"], res.json["psychiatrist"]["id"])
        eq_(True, is_dict_subset_of_superset(psychiatrist, res.json["psychiatrist"]))