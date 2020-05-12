from fiches_urgence.models import Person
from fiches_urgence import db
from config_test import TestApi, client, is_dict_subset_of_superset
from nose.tools import eq_, ok_

#    ___ ___  _  _ _____ ___ ___ ___ _   _ _____ ___ ___  _  _
#   / __/ _ \| \| |_   _| _ \_ _| _ ) | | |_   _|_ _/ _ \| \| |
#  | (_| (_) | .` | | | |   /| || _ \ |_| | | |  | | (_) | .` |
#   \___\___/|_|\_| |_| |_|_\___|___/\___/  |_| |___\___/|_|\_|
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

CONTRIBUTION_RELATIONSHIP = {
    "socialAdvising": True
}


class TestContributionRelationship(TestApi):

    def setUp(self):
        """ Overloads setUp method to automatically create a new Person
        and a new Resident """
        super(TestContributionRelationship, self).setUp()
        res_person = client.post('/persons', json=PERSON)
        RESIDENT["id"] = PERSON["id"] = res_person.json["id"]
        res_resident = client.post('/residents', json=RESIDENT)


    # ---------------- GET ----------------
    def test_get_empty(self):
        res = client.get(
            f'/residents/{RESIDENT["id"]}/contribution-relationships')
        eq_(200, res.status_code)
        eq_([], res.json)

    def test_get_unknwon(self):
        res = client.get(
            f'/residents/{RESIDENT["id"]}/contribution-relationships/unknown')
        eq_(404, res.status_code)

    def test_get_contribution_relationship_id(self):
        res_post = client.post(
            f'/residents/{RESIDENT["id"]}/contribution-relationships',
            json=CONTRIBUTION_RELATIONSHIP
        )
        res = client.get(
            f'/residents/{RESIDENT["id"]}/contribution-relationships/{res_post.json["id"]}')
        eq_(True, is_dict_subset_of_superset(CONTRIBUTION_RELATIONSHIP, res.json))

    # ---------------- POST ----------------
    def test_post_contribution_relationship(self):
        res = client.post(
            f'/residents/{RESIDENT["id"]}/contribution-relationships',
            json=CONTRIBUTION_RELATIONSHIP
        )
        eq_(201, res.status_code)
        eq_(True, is_dict_subset_of_superset(CONTRIBUTION_RELATIONSHIP, res.json))

    # ---------------- PUT ----------------
    def test_put_contribution_relationship(self):
        res_post = client.post(
            f"/residents/{RESIDENT['id']}/contribution-relationships",
            json=CONTRIBUTION_RELATIONSHIP
        )
        new_contribution_relationship = {
            "socialAdvising": False
        }
        res = client.put(
            f"/residents/{RESIDENT['id']}/contribution-relationships/{res_post.json['id']}",
            json=new_contribution_relationship
        )
        eq_(200, res.status_code)
        eq_(
            True,
            is_dict_subset_of_superset(new_contribution_relationship, res.json)
        )

    # ---------------- DELETE ----------------
    def test_delete_contribution_relationship(self):
        res = client.post(
            f"/residents/{RESIDENT['id']}/contribution-relationships",
            json=CONTRIBUTION_RELATIONSHIP
        )
        res = client.delete(
            f"/residents/{RESIDENT['id']}/contribution-relationships/{res.json['id']}")
        eq_(204, res.status_code)
