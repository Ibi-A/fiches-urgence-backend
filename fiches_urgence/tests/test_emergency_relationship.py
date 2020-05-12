from fiches_urgence.models import Person
from fiches_urgence import db
from config_test import TestApi, client, is_dict_subset_of_superset
from nose.tools import eq_, ok_

#   ___ __  __ ___ ___  ___ ___ _  _  _____   __
#  | __|  \/  | __| _ \/ __| __| \| |/ __\ \ / /
#  | _|| |\/| | _||   / (_ | _|| .` | (__ \ V /
#  |___|_|  |_|___|_|_\\___|___|_|\_|\___| |_|
#   ___ ___ _      _ _____ ___ ___  _  _ ___ _  _ ___ ___
#  | _ \ __| |    /_\_   _|_ _/ _ \| \| / __| || |_ _| _ \
#  |   / _|| |__ / _ \| |  | | (_) | .` \__ \ __ || ||  _/
#  |_|_\___|____/_/ \_\_| |___\___/|_|\_|___/_||_|___|_|


PERSON = {
    "firstName": "name",
    "lastName": "name",
    "address": "address"
}

RESIDENT = {
    "birthplace": "yourplace"
}

EMERGENCY_RELATIONSHIP = {
    "relationship": "brother"
}


class TestEmergencyRelationship(TestApi):

    def setUp(self):
        """ Overloads setUp method to automatically create a new Person
        and a Resident """
        super(TestEmergencyRelationship, self).setUp()
        res_person = client.post('/persons', json=PERSON)
        RESIDENT["id"] = PERSON["id"] = res_person.json["id"]
        res_resident = client.post('/residents', json=RESIDENT)

    # -------- GET --------
    def test_get_empty(self):
        res = client.get(
            f'/residents/{RESIDENT["id"]}/emergency-relationships')
        eq_(200, res.status_code)
        eq_([], res.json)

    def test_get_unknwon(self):
        res = client.get(
            f'/residents/{RESIDENT["id"]}/emergency-relationships/unknown')
        eq_(404, res.status_code)

    # -------- POST --------
    def test_post_emergency_relationship(self):
        res = client.post(
            f'/residents/{RESIDENT["id"]}/emergency-relationships',
            json=EMERGENCY_RELATIONSHIP
        )
        eq_(201, res.status_code)
        eq_(True, is_dict_subset_of_superset(EMERGENCY_RELATIONSHIP, res.json))

    # -------- PUT --------
    def test_put_emergency_relationship(self):
        res_post = client.post(
            f"/residents/{RESIDENT['id']}/emergency-relationships",
            json=EMERGENCY_RELATIONSHIP
        )
        new_emergency_relationsship = {
            "relationship": "friend"
        }
        res = client.put(
            f"/residents/{RESIDENT['id']}/emergency-relationships/{res_post.json['id']}",
            json=new_emergency_relationsship
        )
        eq_(200, res.status_code)
        eq_(
            True,
            is_dict_subset_of_superset(new_emergency_relationsship, res.json)
        )

    # -------- DELETE --------
    def test_delete_emergency_relationship(self):
        res = client.post(
            f"/residents/{RESIDENT['id']}/emergency-relationships",
            json=EMERGENCY_RELATIONSHIP
        )
        res = client.delete(
            f"/residents/{RESIDENT['id']}/emergency-relationships/{res.json['id']}")
        eq_(204, res.status_code)