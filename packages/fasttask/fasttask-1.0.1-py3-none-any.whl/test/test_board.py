import unittest
from fasttask.modules.board import Board
from fasttask.modules.task import Task

class TestBoard(unittest.TestCase):

    def setUp(self):
        self.board = Board(board_id=1, name="test_board", label="test")

    def test_add_task(self):
        task = Task(task_id=0, task_name="test_task", status="none",
                creation_date="", label="test", board_id="1", time_worked="0",
                priority=0)

        self.assertTrue(len(self.board.get_all_tasks()) == 0)

        self.board.add_task(task)

        self.assertTrue(len(self.board.get_all_tasks()) == 1)
        self.assertTrue(task in self.board.get_all_tasks())

    def test_update_task_status(self):
        task = Task(task_id=0, task_name="test_task", status="none",
                creation_date="", label="test", board_id="1", time_worked="0",
                priority=0)

        self.board.add_task(task)
        updated_task = self.board.update_task_status(task_name=task.name,
                new_status="todo")
        self.assertTrue(updated_task.status == "todo")

        updated_task = self.board.get_task(task_name=task.name)
        self.assertTrue(updated_task.status == "todo")

    def test_add_two_tasks_and_update_one(self):
        task1 = Task(task_id=0, task_name="test_task1", status="none",
                creation_date="", label="test", board_id="1", time_worked="0",
                priority=0)
        task2 = Task(task_id=1, task_name="test_task2", status="none",
                creation_date="", label="test", board_id="1", time_worked="0",
                priority=0)

        self.board.add_task(task1)
        self.board.add_task(task2)
        self.assertTrue(task2.status == "none")
        self.assertTrue(len(self.board.get_all_tasks()) == 2)

        task2_updated = self.board.update_task_status(task_name=task2.name,
                new_status="todo")
        
        self.assertTrue(task2_updated.status == "todo")

        self.assertTrue(task1 in self.board.get_all_tasks())
        self.assertTrue(task2 in self.board.get_all_tasks())

    def test_delete_task(self):
        task = Task(task_id=0, task_name="test_task", status="none",
                creation_date="", label="test", board_id="1", time_worked="0",
                priority=0)

        self.board.add_task(task)

        self.board.delete_task(task_name=task.name)
        self.assertTrue(len(self.board.get_all_tasks()) == 0)

    def test_add_two_tasks_and_delete_one(self):
        task1 = Task(task_id=0, task_name="test_task1", status="none",
                creation_date="", label="test", board_id="1", time_worked="0",
                priority=0)
        task2 = Task(task_id=1, task_name="test_task2", status="none",
                creation_date="", label="test", board_id="1", time_worked="0",
                priority=0)

        self.board.add_task(task1)
        self.board.add_task(task2)
        self.assertTrue(len(self.board.get_all_tasks()) == 2)

        self.board.delete_task(task_name=task1.name)
        self.assertTrue(len(self.board.get_all_tasks()) == 1)

        
