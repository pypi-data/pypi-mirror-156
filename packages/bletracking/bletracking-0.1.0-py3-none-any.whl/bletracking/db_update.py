import json
import os
import sqlite3
from datetime import datetime

import requests
from dotenv import load_dotenv, find_dotenv

from helpers.BGColor import BGColor
from helpers.SQLite import SQLite

load_dotenv(find_dotenv())

api_url = os.environ.get("API_URL")


def db_update_when_tracker_is_in(data):
    try:
        id = data["id"]
        is_in_area = data["is_in_area"]
        mcid = data["mcid"]
        is_not_in_area = False
        with SQLite('tracker.db') as cur:
            result = cur.execute('SELECT * FROM trackers WHERE id=? AND mcid=? AND is_in_area="IN"', (id, mcid))
            is_not_in_area = result.fetchone() is None
        if is_not_in_area:
            print(f'{datetime.now()} :: {BGColor.OKGREEN}tags state is now activated{BGColor.ENDC}')
            with SQLite('tracker.db') as cur:
                cur.execute(f'''
                    INSERT INTO trackers (id, is_in_area, mcid) VALUES ("{id}", "{is_in_area}", "{mcid}")
                    ON CONFLICT(id) DO UPDATE SET is_in_area="{is_in_area}", mcid="{mcid}"
                ''')
            requests.put(api_url + "/realtime", json={"mcid": mcid, "state": "10"}, verify=False)
            requests.post(f"{api_url}/socket/update-state", json={"message": json.dumps(data, default=str), "channel": "machine-update"}, verify=False)
    except sqlite3.OperationalError as error:
        print(error)
        pass


def db_update_when_tracker_is_out(data):
    try:
        id = data["id"]
        is_in_area = data["is_in_area"]
        mcid = data["mcid"]
        is_still_in_area = False
        with SQLite('tracker.db') as cur:
            result = cur.execute('SELECT * FROM trackers WHERE id=? AND mcid=? AND is_in_area="IN"', (id, mcid))
            is_still_in_area = result.fetchone() is not None

        if is_still_in_area:
            print(f'{datetime.now()} :: {BGColor.WARNING}tags is out of working area{BGColor.ENDC}')
            with SQLite('tracker.db') as cur:
                cur.execute(f'''
                    INSERT INTO trackers (id, is_in_area, mcid) VALUES ("{id}", "{is_in_area}", "{mcid}")
                    ON CONFLICT(id) DO UPDATE SET is_in_area="{is_in_area}", mcid="{mcid}"
                ''')
            requests.put(api_url + "/realtime", json={"mcid": mcid, "state": "30"}, verify=False)
            requests.post(f"{api_url}/socket/update-state", json={"message": json.dumps(data, default=str), "channel": "machine-update"}, verify=False)
    except sqlite3.OperationalError as error:
        print(error)
        pass
