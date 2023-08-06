import random
from datetime import datetime

tracker_list = [
    {
        "id": "a1d11270016a",
        "name": "Demo Zenalyse 1"
    },
    {
        "id": "a1d1127003b4",
        "name": "Demo Zenalyse 2"
    },
    {
        "id": "2100195103a5",
        "name": "Tag Zenalyse"
    }
]


def random_tags():
    tag_size = [1]
    tag_size = random.choice(tag_size)

    current_date = datetime.now()
    current_timestamp = str(datetime.timestamp(current_date) * 1000)[:13]

    random_tracker = random.sample(tracker_list, tag_size)

    result = []
    for i in range(tag_size):
        random_position = [
            0,
            0,
            1.2,
        ]
        result.append({
            "areaId": "TrackingArea1",
            "areaName": "KCM",
            "color": "#0000CC",
            "coordinateSystemId": "CoordinateSystem1",
            "coordinateSystemName": "FirstFloor",
            "covarianceMatrix": [8.9, -3.09, -3.09, 5.56],
            "id": random_tracker[i]["id"],
            "name": random_tracker[i]["name"],
            "position": random_position,
            "positionAccuracy": 1.47,
            "positionTS": current_timestamp,
            "smoothedPosition": random_position,
            "zones": [{
                "id": "Zone005",
                "name": "cashier"
            }]
        })
    return result


def generate_mocked_data():
    current_date = datetime.now()
    current_timestamp = str(datetime.timestamp(current_date) * 1000)[:13]
    tags = random_tags()
    return {
        "code": 0,
        "command": "http://localhost:8080/qpe/getTagPosition?version=2&humanReadable=true&maxAge=5000",
        "message": "Location",
        "responseTS": current_timestamp,
        "status": "Ok",
        "tags": tags,
        "version": "2.1"
    }
