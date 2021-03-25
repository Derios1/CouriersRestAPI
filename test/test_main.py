import unittest
import requests
import json
from datetime import datetime

# For proper testing this tests should be started when tables is empty

START_ID = 10
HOST = "127.0.0.1"
PORT = "8888"
COMPLETE_TIME = ""
ORDER_COUR = {START_ID: START_ID, START_ID + 1: START_ID + 1, START_ID + 2: START_ID + 1,
              START_ID + 3: START_ID, START_ID + 4: START_ID, START_ID + 5: START_ID + 1,
              START_ID + 6: 0}


class TestCouriersLoad(unittest.TestCase):

    def test_usual_load(self):
        data = {'data': [{'courier_id': START_ID, 'courier_type': 'foot',
                          'regions': [100, 101, 102], 'working_hours': ["9:00-13:00", "14:00-20:00"]},
                         {'courier_id': START_ID + 1, 'courier_type': 'bike',
                          'regions': [102, 105, 107], 'working_hours': ["13:00-14:00", "14:15-16:00", "16:21-17:45"]},
                         {'courier_id': START_ID + 2, 'courier_type': 'car',
                          'regions': [101, 105, 111], 'working_hours': ["19:00-23:00"]}
                         ]
                }

        resp = requests.post("http://{}:{}/couriers".format(HOST, PORT), data=json.dumps(data))
        resp_content = json.loads(resp.json())
        self.assertEqual(resp.status_code, 201)
        for i in range(3):
            self.assertEqual(resp_content["couriers"][i]['id'], START_ID + i)

    def test_invalid_load_index(self):
        data = {'data': [{'courier_id': START_ID, 'courier_type': 'foot',
                          'regions': [100, 101, 102], 'working_hours': ["9:00-13:00", "14:00-20:00"]}
                         ]
                }

        resp = requests.post("http://{}:{}/couriers".format(HOST, PORT), data=json.dumps(data))
        self.assertEqual(resp.status_code, 400)

    def test_invalid_load_type(self):
        data = {'data': [{'courier_id': START_ID + 5, 'courier_type': 'airplane',
                          'regions': [100, 101, 102], 'working_hours': ["9:00-13:00", "14:00-20:00"]}
                         ]
                }

        resp = requests.post("http://{}:{}/couriers".format(HOST, PORT), data=json.dumps(data))
        self.assertEqual(resp.status_code, 400)

    def test_invalid_load_region(self):
        data = {'data': [{'courier_id': START_ID + 5, 'courier_type': 'foot',
                          'regions': [-100, -101, 102], 'working_hours': ["9:00-13:00", "14:00-20:00"]}
                         ]
                }
        resp = requests.post("http://{}:{}/couriers".format(HOST, PORT), data=json.dumps(data))
        self.assertEqual(resp.status_code, 400)

    def test_invalid_load_time(self):
        data = {'data': [{'courier_id': START_ID + 5, 'courier_type': 'foot',
                          'regions': [100, 101, 102], 'working_hours': ["9:00-26:00", "14:00-20:00"]}
                         ]
                }

        resp = requests.post("http://{}:{}/couriers".format(HOST, PORT), data=json.dumps(data))
        self.assertEqual(resp.status_code, 400)


class TestOrdersLoad(unittest.TestCase):

    def test_usual_load(self):
        data = {'data': [{'order_id': START_ID, 'weight': 1.5,
                          'region': 100, 'delivery_hours': ["14:00-15:00"]},
                         {'order_id': START_ID + 1, 'weight': 2.35,
                          'region': 107, 'delivery_hours': ["15:00-16:00", "20:00-20:30"]},
                         {'order_id': START_ID + 2, 'weight': 5.42,
                          'region': 102, 'delivery_hours': ["19:00-20:00", "10:00-12:00"]},
                         {'order_id': START_ID + 3, 'weight': 3.76,
                          'region': 100, 'delivery_hours': ["10:00-20:00"]},
                         {'order_id': START_ID + 4, 'weight': 1.99,
                          'region': 102, 'delivery_hours': ["10:00-20:00"]},
                         {'order_id': START_ID + 5, 'weight': 1.99,
                          'region': 105, 'delivery_hours': ["15:00-16:00", "17:00-19:00", "20:00-21:35"]},
                         {'order_id': START_ID + 6, 'weight': 13.39,
                          'region': 112, 'delivery_hours': ["15:11-16:23", "11:00-12:05", "20:00-21:35"]}
                         ]
                }

        resp = requests.post("http://{}:{}/orders".format(HOST, PORT), data=json.dumps(data))
        resp_content = json.loads(resp.json())
        print(resp_content)
        self.assertEqual(resp.status_code, 201)
        for i in range(3):
            self.assertEqual(resp_content["orders"][i]['id'], START_ID + i)


class TestOrderAssign(unittest.TestCase):

    def test_usual_assign(self):
        data = {"courier_id": START_ID}
        resp = requests.post("http://{}:{}/orders/assign".format(HOST, PORT), data=json.dumps(data))

        self.assertEqual(resp.status_code, 200)
        resp_content = json.loads(resp.json())
        print(resp_content)
        self.assertEqual(resp_content["orders"], [{'id': START_ID}, {'id': START_ID + 4},
                                                  {'id': START_ID + 3}])  # sorted by weight

        data = {"courier_id": START_ID + 1}
        resp = requests.post("http://{}:{}/orders/assign".format(HOST, PORT), data=json.dumps(data))
        self.assertEqual(resp.status_code, 200)
        resp_content = json.loads(resp.json())
        print(resp_content)
        self.assertEqual(resp_content["orders"], [{'id': START_ID + 5}, {'id': START_ID + 1}, {'id': START_ID + 2}])

        data = {"courier_id": START_ID + 2}
        resp = requests.post("http://{}:{}/orders/assign".format(HOST, PORT), data=json.dumps(data))
        self.assertEqual(resp.status_code, 200)
        resp_content = json.loads(resp.json())
        print(resp_content)
        self.assertEqual(len(resp_content["orders"]), 0)
        self.assertTrue(resp_content.get('assign_time') is None)


class TestCourierInfoUpd(unittest.TestCase):

    def test_info_upd(self):
        data = {'working_hours': ["9:00-13:01", "14:00-20:00"]}
        resp = requests.patch("http://{}:{}/couriers/{}".format(HOST, PORT, START_ID), data=json.dumps(data))
        resp_content = json.loads(resp.json())
        self.assertEqual(resp_content['working_hours'], ["9:00-13:01", "14:00-20:00"])

    def test_with_reassigning_time(self):
        data = {'working_hours': ["9:00-13:01", "17:00-20:00"]}
        resp = requests.patch("http://{}:{}/couriers/{}".format(HOST, PORT, START_ID), data=json.dumps(data))


class TestOrderComplete(unittest.TestCase):

    def test_usual_complete(self):

        if COMPLETE_TIME == '':
            time = datetime.now().isoformat() + 'Z'
        else:
            time = COMPLETE_TIME

        for i in range(7):
            data = {'courier_id': ORDER_COUR[START_ID + i], 'order_id': START_ID + i, 'complete_time': time}
            resp = requests.post("http://{}:{}/orders/complete".format(HOST, PORT), data=json.dumps(data))
            if i in [6, 0]:
                self.assertEqual(resp.status_code, 400)
            else:
                resp_content = json.loads(resp.json())
                self.assertEqual(resp_content['order_id'], START_ID + i)
                self.assertEqual(resp.status_code, 200)


class TestCourierInfo(unittest.TestCase):

    def test_info(self):
        for i in range(3):
            resp = requests.get("http://{}:{}/couriers/{}".format(HOST, PORT, START_ID + i))
            resp_content = resp.json()
            print(resp_content)
