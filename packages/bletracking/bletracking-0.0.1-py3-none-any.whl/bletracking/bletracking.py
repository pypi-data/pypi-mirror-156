import json
import os
from time import sleep

import requests
import typer as typer
import urllib3
from dotenv import find_dotenv, load_dotenv

from bletracking.check_area_entering import check_area_entering
from bletracking.db_init import db_init
from bletracking.generate_mocked_data import generate_mocked_data
from bletracking.publish_to_socket import publish_to_socket

urllib3.disable_warnings()

load_dotenv(find_dotenv())

api_url = os.environ.get("API_URL")
qpe_url = os.environ.get("QPE_URL")

app = typer.Typer()


@app.command()
def bletracking(mode, refresh_rate):
    try:
        db_init()
        area_list = requests.get(api_url + "/area/list", verify=False)
        area_list = json.loads(area_list.text)
        area_list = area_list['result']
        while True:
            try:
                if mode == "production":
                    data_from_qpe = requests.get(qpe_url, verify=False, timeout=1)
                    data_from_qpe = json.loads(data_from_qpe.text)
                else:
                    data_from_qpe = generate_mocked_data()

                publish_to_socket(data_from_qpe)
                check_area_entering(data_from_qpe, area_list)
                sleep(refresh_rate)
            except Exception as error:
                print(error)
                pass
    except Exception as error:
        print(error)


if __name__ == '__main__':
    app()
