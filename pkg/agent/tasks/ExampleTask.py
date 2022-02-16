import time
from pkg.agent.tasks.CTTask import CTTask, TaskNames


class ExampleTask(CTTask):
    def get_name(self):
        return TaskNames.ExampleTask

    def run_task(self):
        print(" [x] Running ExampleTask...")
        time.sleep(12)
        print(" [x] Done")


