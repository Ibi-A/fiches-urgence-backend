from fiches_urgence.models import Person
from fiches_urgence import db
from config_test import TestApi, client
from nose.tools import eq_, ok_

#   _  _ ___   _   _  _____ _  _    __  __ _   _ _____ _   _  _   _    
#  | || | __| /_\ | ||_   _| || |  |  \/  | | | |_   _| | | |/_\ | |   
#  | __ | _| / _ \| |__| | | __ |  | |\/| | |_| | | | | |_| / _ \| |__ 
#  |_||_|___/_/ \_\____|_| |_||_|  |_|  |_|\___/  |_|  \___/_/ \_\____|
                                                                     


HEALTH_MUTUAL = {
    "name": "health",
    "address": "mutual",
    "mainPhoneNumber": "012345678",
    "alternativePhoneNumber": "09876543"
}


class TestHealthMutual(TestApi):

    def test_get_health_mutuals(self):
        res = client.get('/health-mutuals')
        eq_(200, res.status_code)
        eq_([], res.json)

    def test_get_unknwon(self):
        res = client.get('/health-mutuals/unknown')
        eq_(404, res.status_code)

    def test_post_health_mutuals_no_data(self):
        res = client.post('/health-mutuals')
        eq_(400, res.status_code)

    def test_post_health_mutuals(self):
        res = client.post('/health-mutuals', json=HEALTH_MUTUAL)

        eq_(201, res.status_code)
        HEALTH_MUTUAL["id"] = res.json["id"]
        eq_(HEALTH_MUTUAL, res.json)

        res = client.get(f'/health-mutuals/{HEALTH_MUTUAL["id"]}')
        eq_(200, res.status_code)
        eq_(HEALTH_MUTUAL, res.json)

    def test_put_health_mutual(self):
        res_post = client.post('/health-mutuals', json=HEALTH_MUTUAL)
        new_health_mutual = {
            "name": "nameHealth",
            "address": "addressMutual",
            "mainPhoneNumber": "11111111",
            "alternativePhoneNumber": "22222222"
        }
        res = client.put(
            f'/health-mutuals/{res_post.json["id"]}', json=new_health_mutual)
        new_health_mutual["id"] = res_post.json["id"]
        eq_(200, res.status_code)
        eq_(new_health_mutual, res.json)

    def test_delete_health_mutual(self):
        res_post = client.post('/health-mutuals', json=HEALTH_MUTUAL)
        res = client.delete(f"/health-mutuals/{res_post.json['id']}")
        eq_(204, res.status_code)
