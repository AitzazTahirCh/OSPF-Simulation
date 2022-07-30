from actions import *

_help_str = '''
Demonstrate "Open Shortest Path First protocol" work
Commands:
  `add x y`    adds router with (x, y) position, x and y must be float in range [0; 1]
  `ping start_id finish_id`    transits way from router node to another throw shortest path, ids must be int
  `scenario scenarioName`   adds couple of routers, scenarioName must be one of 'circle', 'polygon' or  'mill'
  `help`    prints help information
  `exit`    correct program terminates 
'''

def form_action(args):
    name = args[0]
    if name == 'add':
        return AddAction(float(args[1]), float(args[2]))
    elif name == 'scenario':
        scenario_names ={
            'circle': ScenarioCircle,
            'polygon': ScenarioPolygon,
            'mill': ScenarioMill
        }

        if args[1] not in scenario_names.keys():
            print('Wrong command, print \"help\" for information')
            return Action()

        return scenario_names[args[1]]()

    if name == 'ping':
        return PingAction(int(args[1]), int(args[2]))
    if name == 'help':
        print(_help_str)
        return Action()
    elif name == 'exit':
        return ExitAction()


def parse_args(args: list):
    commands = {
        'scenario': 1,
        'ping': 2,
        'add': 2,
        'help': 0,
        'exit': 0
    }

    command = args[0]
    if command not in commands.keys():
        print('Wrong command, print \"help\" for information')
        return Action()

    action_info = commands.get(command)
    if len(args) - 1 != action_info:
        print('Wrong parameters number, print \"help\" for information')
        return Action()

    return form_action(args)


def cmd_parse(str_action: str):
    try:
        action = parse_args(str_action.strip('\n').split(' '))
        return action

    except SystemExit:
        pass