from typing import List


from fasttask.modules.task import Task

class Board:
    def __init__(self, board_id: int, name: str, label: str = ""):
        self.board_id = board_id
        self.name = name
        self.label = label
        self.tasks: List[Task] = []

    def get_board_id(self) -> int:
        return self.board_id

    def get_board_name(self) -> str:
        return self.name

    def get_board_label(self) -> str:
        return self.label


    def get_all_tasks(self):
        return self.tasks

    def get_task(self, task_name: str):
        for task in self.tasks:
            if task.name == task_name:
                return task

        return None #@TODO: Throw exception TaskNotFound

    def add_task(self, task: Task):
        self.tasks.append(task)

    def update_task_status(self, task_name: str, new_status: str) -> bool:
        for task in self.tasks:
            if task.name == task_name:
                task.update_status(new_status)
                return task

        return None #@TODO: Throw exception TaskNotFound

    def delete_task(self, task_name: str):
        self.tasks = list(filter(lambda task: (
            task.name != task_name), self.tasks))

# Print tasks should be moved to CLI
#     def print_task(self, task_name: str):
#         for task in self.tasks:
#             if task.name == task_name:
#                 task.print_task()
#                 return
# 
#         print(f'Task {task_name} not found :(')


# Prints tasks in an array of tasks
# for task in self.tasks:
#     print(
#         f'{task.task_name} {task.status} {task.creation_date} {task.priority}')