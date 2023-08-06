import time

import requests
from rich.console import Console
from rich.live import Live
from rich.pretty import pprint
from rich.table import Table

from stresstest.sensors import collect
from stresstest.stresstest import BaseStresstest

SERVER_URL = "https://us-central1-iron-envelope-354712.cloudfunctions.net/collect"


console = Console()


class Runner:
    def run(self, dont_send: bool):
        sensor_data = collect()

        table = Table()
        table.add_column("Test name")
        table.add_column("Duration")

        test_results = []

        with Live(table, refresh_per_second=4):  # update 4 times a second to feel fluid
            for test in BaseStresstest.discover():
                test_instance = test()
                test_name = " / ".join(test_instance.name)

                try:
                    parameters = {
                        p.name: p.get_value() for p in test_instance.parameters
                    }

                    test_instance.run_test(**parameters)
                    test_duration = test_instance.time()

                    table.add_row(f"[green]{test_name}", f"{test_duration:.6f}")
                    test_results.append(
                        {
                            "name": test_name,
                            "duration": test_duration,
                        }
                    )
                except Exception as e:
                    table.add_row(f"[red]{test_name}", "")
                    test_results.append(
                        {
                            "name": test_name,
                            "duration": "",
                        }
                    )

        if not dont_send:
            console.print(
                "[red]Collected data will be sent to server [bold]in 3 seconds[/bold] (use [italic]--dont-send[/italic] to avoid this) ..."
            )
            time.sleep(3)
            json_data = {
                "sensor_data": sensor_data,
                "test_results": test_results,
            }
            response = requests.post(SERVER_URL, json=json_data)
            if response.status_code == 200:
                response_json = response.json()
                collection_id = response_json.get("collection_id")
                if collection_id:
                    console.print(
                        f"Collected data successfully sent to server with collection ID:\n[italic]{collection_id}[/italic]"
                    )
