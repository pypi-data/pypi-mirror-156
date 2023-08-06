import json
import os
from datetime import datetime

import requests
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

api_url = os.environ.get("API_URL")


def publish_to_socket(data_from_qpe):
    try:
        requests.post(f"{api_url}/socket/update-position", data={"message": json.dumps(data_from_qpe, default=str), "channel": "tracker-update"}, verify=False)
        print(f'{datetime.now()} :: {len(data_from_qpe["tags"])} tags location was published via socket')

    except Exception as error:
        print(error)
        pass
