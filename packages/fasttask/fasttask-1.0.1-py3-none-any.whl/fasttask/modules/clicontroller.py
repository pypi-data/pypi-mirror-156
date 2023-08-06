import configparser
import os
from typing import Callable, List

from fasttask.modules.cmd_example import example_cmd
from fasttask.modules.command import Command
from fasttask.modules.dbhandler import DBHandler


class CLI:
    def __init__(self):
        self._config_file = os.path.expanduser('~') + '/.fasttaskrc'
        self.config = configparser.ConfigParser()
        self.config.read(self._config_file)
        self.dbh = DBHandler()

        if(len(self.config.sections()) == 0):
            self.config.add_section('Settings')
            default_board = self.dbh.create_board('Default', '')
            self.config.set('Settings', 'board', str(default_board.board_id))
            self.config.set('Settings', 'max_work_session', '8')
            self.save_configs()
            self.board = default_board
            self._board = default_board.board_id
            self._max_work_session = 8
        else:
            self._board = int(self.config.get('Settings', 'board'))
            self._max_work_session = int(
                self.config.get('Settings', 'max_work_session'))
            self.board = self.dbh.get_board(self._board)

        # flag variables
        self._reset_flags()

    def save_configs(self):
        with open(self._config_file, 'w') as configfile:
            self.config.write(configfile)

    def _reset_flags(self):
        self.label_flag_value:str = ''
        self.priority_flag_value:int = 0

    def main(self):
        board_create_cmd = Command("create").with_args(self.board_create(), 1) \
             .with_flag('label', 'lb', self.label_flag(), True)
        board_list_cmd = Command("list").with_no_args(self.board_list())
        board_checkout_cmd = Command(
            "checkout").with_args(self.board_checkout(), 1)
        board_delete_cmd = Command("delete").with_args(self.board_delete(), 1)

        board_cmd = Command("board") \
            .with_sub_command(board_create_cmd) \
            .with_sub_command(board_list_cmd) \
            .with_sub_command(board_checkout_cmd) \
            .with_sub_command(board_delete_cmd)
        
        task_create_cmd = Command('create').with_args(self.task_create(), 1) \
            .with_flag('label', 'lb', self.label_flag(), True) \
            .with_flag('priority', 'pr', self.priority_flag(), True) 
        task_update_cmd = Command('update').with_args(self.task_update(), 2)
        task_describe_cmd = Command('describe').with_args(self.task_describe(), 1)
        task_list_cmd = Command('list').with_no_args(self.task_list())

        task_cmd = Command('task') \
                .with_sub_command(task_create_cmd) \
                .with_sub_command(task_update_cmd) \
                .with_sub_command(task_describe_cmd) \
                .with_sub_command(task_list_cmd)

        self.command = Command('fasttask') \
            .with_sub_command(board_cmd) \
            .with_sub_command(task_cmd)

        self.command.run()

    def board_create(self):
        def board_create_cmd(data: List[str]) -> None:
            new_boar_id = self.dbh.create_board(data[0], self.label_flag_value)
            self.board = self.dbh.get_board(new_boar_id)
            self._reset_flags()

        return board_create_cmd

    def board_list(self):
        def board_list_cmd() -> None:
            boards = self.dbh.get_boards()
            for board in boards:
                print(board[1], f'(id={board[0]})')

        return board_list_cmd

    def board_checkout(self):
        def board_checkout_cmd(data: List[str]) -> None:
            try:
                board_id = int(data[0])
            except:
                print('board checkout parameter must be a board id')
                return
            self.board = self.dbh.get_board(board_id)
            self.config.set('Settings', 'board', str(self.board.board_id))
            self.save_configs()

        return board_checkout_cmd

    def board_delete(self):
        def board_delete_cmd(data: List[str]) -> None:
            board_id = int(data[0])
            if self.board.get_board_id() != board_id:
                self.dbh.delete_board(board_id)

        return board_delete_cmd

    def task_create(self) -> Callable[[List[str]], None]:
        def task_create_cmd(args: List[str]) -> None:
            new_task = self.dbh.create_task(self._board, args[0], self.label_flag_value, self.priority_flag_value)
            self.board.add_task(new_task)
            print(f'Task {new_task.name} successfuly created!')
            self._reset_flags()
        return task_create_cmd

    def label_flag(self) -> Callable[[str], None]:
        def set_label_flag(label: str) -> None:
            self.label_flag_value = label
        return set_label_flag
    
    def priority_flag(self) -> Callable[[str], None]:
        def set_priority_flag(priority: str) -> None:
            self.priority_flag_value = int(priority)
        return set_priority_flag
    
    def task_update(self) -> Callable[[List[str]], None]:
        def task_update_cmd(args: List[str]) -> None:
            task = self.board.get_task(args[0])
            self.dbh.update_task(task.id, args[1])
            task.update_status(args[1])
            print(f'Task status updated tp {args[1]}')
        return task_update_cmd
    
    def task_describe(self) -> Callable[[List[str]], None]:
        def task_describe_cmd(args: List[str]) -> None:
            task = self.board.get_task(args[0])
            print("Task details:")
            print('Id: ', task.id)
            print("Name: ", task.name)
            print("Status: ", task.status)
            print("Creation date: ", task.creation_date)
            print("Label: ", task.label)
            print("Priority: ", task.priority)
            print("Time Worked in this task: ", task.time_worked, "\n")
        return task_describe_cmd

    def task_list(self) -> Callable[[], None]:
        def task_list_cmd() -> None:
            print('On', self.board.get_board_name(), f'(id={self.board.board_id}):')
            for task in self.board.get_all_tasks():
                print(task.name)
        return task_list_cmd
