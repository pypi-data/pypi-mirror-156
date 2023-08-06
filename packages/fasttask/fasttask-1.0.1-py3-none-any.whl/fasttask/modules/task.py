import typing

class Task:
    def __init__(self, task_id: int, task_name: str, status: str,
            creation_date: str, label: str, board_id: int, time_worked: int = 0,
            priority: int =0):
        self.id       = task_id
        self.name     = task_name
        self.status        = status
        self.creation_date = creation_date
        self.label         = label
        self.board_id      = board_id
        self.time_worked   = time_worked
        self.priority      = priority

    def update_status(self, new_status: str):
        self.status = new_status

    def get_task_details(self):
        return {
                "id": self.id,
                "name": self.name,
                "status": self.status,
                "creation_date": self.creation_date,
                "label": self.label,
                "board_id": self.board_id,
                "time_worked": self.time_worked,
                "priority": self.priority
        }

    def start_working(self):
        pass

    def stop_working(self):
        pass

