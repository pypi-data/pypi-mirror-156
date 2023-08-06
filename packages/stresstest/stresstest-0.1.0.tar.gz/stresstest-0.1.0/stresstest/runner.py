import time

from rich.live import Live
from rich.pretty import pprint
from rich.table import Table

from stresstest.sensors import collect
from stresstest.stresstest import BaseStresstest


class Runner:
    def run(self):
        sensor_data = collect()
        pprint(sensor_data)

        table = Table()
        table.add_column("Test name")
        table.add_column("Duration")

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
                except Exception as e:
                    table.add_row(f"[red]{test_name}", "")
                    print(e)
