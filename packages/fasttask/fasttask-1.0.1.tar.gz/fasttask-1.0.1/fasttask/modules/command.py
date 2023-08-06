import sys
from typing import Callable, Dict, List


class CommandEnd(Exception):
    pass


class Command:
    def __init__(self, handle: str):
        self.handle: str = handle
        self.description: str = handle + ' help'
        self.exec: Callable[[List[str]],
                            None] = zero_args_command_function(self.help)
        self.argc: int = 0
        self.argv: List[str] = []
        self.sub_commands: Dict[str, Command] = {}
        self.flags: Dict[str, Callable] = {}
        self.shorts: Dict[str, str] = {}
        self.flag_has_parameter: Dict[str, bool] = {}
        self.shell_prefix: str = "> "

    def with_descryption(self, descrption):
        self.description = descrption
        return self

    def with_args(self, exec: Callable[[List[str]], None], argc: int):
        if len(self.sub_commands) != 0:
            raise Exception(
                'Error: this command has sub operations, it can\'t also execute a function with parameters.')
        self.exec = exec
        self.argc = argc
        return self

    def with_no_args(self, exec: Callable[[], None]):
        self.exec = zero_args_command_function(exec)
        return self

    def with_sub_command(self, sub_command):
        if type(sub_command) != type(self):
            raise Exception(
                'Error: type error sub_commant must be a Command object. ')
        sub_handle = sub_command.handle
        if sub_handle in self.flags:
            raise Exception(f'Error: {sub_handle} flag already exists.')
        if self.argc != 0:
            raise Exception(
                'Error: this command takes parameters, it can\'t also support sub commands.')
        sub_command.shell_prefix = ' ' + self.shell_prefix
        self.sub_commands[sub_handle] = sub_command
        return self

    def with_flag(self, flag_handle: str, flag_short: str, flag_execute: Callable, takes_parameter: bool = False):
        if flag_handle in self.flags:
            raise Exception(f'Error: {flag_handle} flag already exists.')
        flag_handle = '--' + flag_handle
        self.shorts['-' + flag_short] = flag_handle
        self.flags[flag_handle] = flag_execute
        self.flag_has_parameter[flag_handle] = takes_parameter
        return self

    def help(self):
        print(self.description)

    def set_argv(self, argv):
        self.argv = argv

    def run(self):
        self.argv = sys.argv
        if self.handle != self.parse_system_call():
            self.help()
            return
        try:
            self.parse()
        except Exception as _:
            return

    def parse_system_call(self) -> str:
        return self.consume().split('/')[-1]

    def consume(self) -> str:
        argument = ''
        if len(self.argv) > 0:
            argument = self.argv[0]
            self.argv = self.argv[1:]
        return argument

    def parse(self):
        if self.super():
            self.parse_super()
        else:
            self.parse_command()

    def parse_super(self):
        if len(self.argv) == 0:
            self.shell()
            return
        sub_handle = self.consume()
        if sub_handle not in self.sub_commands:
            self.help()
            raise Exception('Error')
        sub_command = self.sub_commands[sub_handle]
        sub_command.set_argv(self.argv)
        self.argv = []
        sub_command.parse()

    def parse_command(self):
        if len(self.argv) < self.argc:
            self.help()
            raise Exception('Error')
        arguments = self.get_arguments()
        for argument in arguments:
            if self.is_flag(argument):
                self.help()
                raise Exception('Error')
        self.parse_flags()
        self.exec(arguments)

    def super(self) -> bool:
        return len(self.sub_commands) != 0

    def shell(self):
        self.run_shell = True
        while(self.run_shell):
            self.argv  += input(self.shell_prefix).split(' ')
            if not self.shell_interupt():
                try:
                    self.parse()
                except CommandEnd:
                    return
                except Exception:
                    self.consume()
    
    def shell_interupt(self) -> bool:
        if self.argv[0] == 'help':
                self.help()
                self.consume()
                return True
        
        elif self.argv[0] == 'quit' or self.argv[0] == 'exit':
                self.run_shell = False
                self.consume()
                return True
                
        return False

    def get_arguments(self) -> List[str]:
        arguments = []
        for _ in range(self.argc):
            arguments.append(self.consume())
        return arguments

    def is_flag(self, argument: str) -> bool:
        return argument[0] == '-'

    def sanitize_flags(self, argument):
        if not self.is_flag(argument):
            self.help()
            raise Exception('Error')

        if argument in self.shorts:
            argument = self.shorts[argument]

        if argument not in self.flags:
            self.help()
            raise Exception('Error')

        return argument


    def parse_flags(self):
        argument = self.consume()
        while(argument != ''):
            try:
                argument = self.sanitize_flags(argument)
                flag_exec = self.flags[argument]

                if self.flag_has_parameter[argument]:
                    flag_exec(self.consume())
                else:
                    flag_exec()

                argument = self.consume()
            except Exception as e:
                print(e)



def zero_args_command_function(func: Callable[[], None]) -> Callable[[List[str]], None]:
    def new_func(_: List[str]):
        func()
    return new_func
