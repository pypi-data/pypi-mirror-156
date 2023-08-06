from fasttask.modules.command import Command, List

flag_a = ''

flag_b = ''

def param_example(parameters:  List[str]) -> None:
    print(f'this command takes a parameter: {parameters}\nflag_a: {flag_a}\nflag_b: {flag_b}')

def noparam_example() -> None:
    print(f'this command does not take parameters\nflag_a: {flag_a}\nflag_b: {flag_b}')

def set_flag_a(parameter: str):
    global flag_a
    flag_a = parameter

def set_flag_b():
    global flag_b
    flag_b = 'set'

param_example_cmd = Command('param') \
                                    .with_args(param_example,1) \
                                    .with_flag('aflag', 'af', set_flag_a, True) \
                                    .with_flag('bflag', 'bf', set_flag_b)
noparam_example_cmd = Command('noparam') \
                                    .with_no_args(noparam_example) \
                                    .with_flag('aflag', 'af', set_flag_a, True) \
                                    .with_flag('bflag', 'bf', set_flag_b)
example_cmd = Command('example').with_sub_command(param_example_cmd).with_sub_command(noparam_example_cmd)