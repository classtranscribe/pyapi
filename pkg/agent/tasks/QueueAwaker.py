from pkg.agent.tasks.CTTask import CTTask, TaskNames


class QueueAwaker(CTTask):
    def get_name(self):
        return TaskNames.QueueAwaker

    def run_task(self):
        print(" [x] Running ExampleTask...")
        print(" [x] Done")
