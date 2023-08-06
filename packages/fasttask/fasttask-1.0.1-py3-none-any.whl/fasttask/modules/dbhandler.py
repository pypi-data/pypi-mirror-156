import os
import sqlite3
from sqlite3 import Error
from datetime import date

from fasttask.modules.board import Board
from fasttask.modules.task import Task


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DBHandler(metaclass=Singleton):

    def __init__(self):
        default_db_file = os.path.expanduser('~') + '/.fasttaskdb'
        self.conn = self._create_connection(default_db_file)
        self.cur = self.conn.cursor()

        self._setup_database()

    def _create_connection(self, db_file):
        connection = None
        try:
            connection = sqlite3.connect(db_file)
            return connection
        except Error as e:
            print("Unable to connect to the database")
            print(e)

    def _setup_database(self):
        sql = """create table if not exists boards (
            id integer primary key autoincrement,
            name text,
            label text
        )"""
        self.cur.execute(sql)

        sql = """create table if not exists tasks (
            id integer primary key autoincrement,
            board_id integer,
            name text,
            status text,
            creation_date text,
            label text,
            time_worked text,
            priority integer,
            foreign key(board_id) references board(id)
        )"""

        self.cur.execute(sql)

    def get_connection(self):
        return self.conn

    # Returns a list of (int,string,string) with the (id,name,label) of each board
    def get_boards(self):
        sql = 'select * from boards'

        self.cur.execute(sql)
        boards = self.cur.fetchall()

        return boards

    # Receives board data and returns an instance of the board
    def _load_board(self, board_data, tasks_data):
        board_id = board_data[0]
        board_name = board_data[1]
        board_label = board_data[2]
        # ID, name, and tag, respectively
        board = Board(board_id, board_name, board_label)

        for task in tasks_data:
            task_id = task[0]
            task_name = task[1]
            task_status = task[2]
            task_creation_date = task[3]
            task_label = task[4]
            task_time_worked = task[5]
            task_priority = task[6]
            task_board_id = task[7]
            board_task = Task(task_id, task_name, task_status,
                              task_creation_date, task_label, task_board_id,
                              task_time_worked, task_priority)
            board.add_task(board_task)
        return board

    # Returns a board object with all tasks already populated
    def get_board(self, board_id):
        params = (board_id,)

        sql = 'select id,name,label from boards where id = ?'
        self.cur.execute(sql, params)
        board_data = self.cur.fetchall()[0]

        sql = """select
            id,
            name,
            status,
            creation_date,
            label,
            time_worked,
            priority,
            board_id
            from tasks where board_id = ?"""

        self.cur.execute(sql, params)
        tasks_data = self.cur.fetchall()

        board = self._load_board(board_data, tasks_data)

        return board

    # Returns the newly created board
    def create_board(self, board_name: str, board_label: str) -> Board:
        params = (board_name, board_label)

        sql = """insert into boards
            (name, label)
            values
            (?,?)"""

        self.cur.execute(sql, params)
        self.conn.commit()

        return self.get_board(self.cur.lastrowid)

    def delete_board(self, board_id: int):
        params = (board_id,)

        sql = 'delete from boards where id = ?'

        self.cur.execute(sql, params)
        self.conn.commit()

    def get_task(self, task_id):
        params = (task_id,)

        sql = """select
            id,
            name,
            status,
            creation_date,
            label,
            time_worked,
            priority,
            board_id
            from tasks where id = ?"""

        self.cur.execute(sql, params)
        task_data = self.cur.fetchall()[0]
        task_id = task_data[0]
        task_name = task_data[1]
        task_status = task_data[2]
        task_creation_date = task_data[3]
        task_label = task_data[4]
        task_time_worked = task_data[5]
        task_priority = task_data[6]
        task_board_id = task_data[7]
        task = Task(task_id, task_name, task_status,
                    task_creation_date, task_label, task_board_id,
                    task_time_worked, task_priority)

        return task

    # Returns the ID of the newly created task
    def create_task(self, board_id: int, task_name: str, label: str = '', priority: int = 0) -> Task:
        creation_date: str = date.today().strftime('%d/%m/%Y')
        status: str = 'ToDo'
        time_worked: int = 0
        params = (task_name,
                  status,
                  creation_date,
                  label,
                  time_worked,
                  priority,
                  board_id)

        sql = """insert into tasks
            (name, status, creation_date, label, time_worked, priority,
            board_id)
            values
            (?,?,?,?,?,?,?)"""

        self.cur.execute(sql, params)
        self.conn.commit()

        return self.get_task(self.cur.lastrowid)

    # Returns TRUE if task was updated successfully, FALSE otherwise
    def update_task(self, task_id: int, new_status: str):
        params = (new_status, task_id)

        sql = """update tasks
            set status = ?
            where id = ?
        """

        self.cur.execute(sql, params)
        self.conn.commit()

    # Returns TRUE if task was deleted successfully, FALSE otherwise
    def delete_task(self, task_id: int):
        params = (task_id,)

        sql = 'delete from tasks where id = ?'

        self.cur.execute(sql, params)
        self.conn.commit()
