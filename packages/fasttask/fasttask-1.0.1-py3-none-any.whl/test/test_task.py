import unittest
from fasttask.modules.task import Task

class TestTask(unittest.TestCase):
    def setUp(self):
        self.task = Task(task_id=0, task_name="test_task", status="none",
                creation_date="", label="test", board_id="1", time_worked="0",
                priority=0)

    def test_get_task_details(self):
        self.task.get_task_details()

        self.assertTrue(self.task.get_task_details()["id"] == self.task.id)
        self.assertTrue(self.task.get_task_details()["name"] == self.task.name)
        self.assertTrue(self.task.get_task_details()["status"] == self.task.status)

    def test_update_status(self):
        new_status = "todo"
        self.task.update_status(new_status)

        self.assertTrue(self.task.get_task_details()["status"] == "todo")
    
    

