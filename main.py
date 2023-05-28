import json
import os
import shutil
import supported_command

# init global variables
vulnerability_name = ''
helps = {}
command_list = supported_command.command_list
tenv_fileRestrictions = []


def build_tenv(config: dict):
    """
    :param config: the config file 'tenv.config.json' as a dict.
    :return: None
    """

    def helper(curr_path: str, folder: dict, father_flag: str):
        for name in folder:
            # get content.
            content = folder[name]

            # get flags.
            name = name.split('#') + [father_flag]
            name, flag = name[0], name[1]

            if name[0] == '!':  # special command
                content_type = name[1:content.find('!', 1) - 1]

                if content_type == 'FILE':
                    shutil.copy('vulnerabilities/{}/files/{}'.format(vulnerability_name, content), curr_path)
            else:
                os.mkdir(curr_path + name)

                # write flags.
                with open(curr_path + name + "/.config", 'w') as f:
                    f.write(flag)

                helper(curr_path + name + "/", content, flag)

    helper('tenv/', config['tree'], 'rwx')
    # write flags for tenv.
    with open("tenv/.config", 'w') as f:
        f.write('rwx')



def destroy_tenv():
    # remove tenv
    shutil.rmtree('tenv')
    os.mkdir('tenv')


def print_help(title: str, content):
    if isinstance(content, str):
        return title.upper() + "\n  " + content.strip().replace('\n', '\n  ')
    elif isinstance(content, dict):
        c = ''
        for t in content:
            c += print_help(t, content[t]) + '\n'
        return title.upper() + "\n  " + c.strip().replace('\n', '\n  ')
    else:
        raise Exception('Error 0x001')


def get_help(help_file):
    global helps
    helps = help_file
    for title in helps:
        if title[0] != '-':
            print(print_help(title, helps[title]))
            print()


def run_command(curr_dir, cmd):
    cmd[0] = cmd[0].lower()
    if cmd[0] == 'help' and len(cmd) == 2:
        with open("vulnerabilities/{}/help.json".format(vulnerability_name)) as f:
            try:
                help_content = json.load(f)['-' + cmd[1]]
                print('@' * 30)
                print(print_help(cmd[1], help_content))
                print('@' * 30)
            except KeyError:
                print('Help not found.')
    elif cmd[0] == 'exit':
        global keep_running
        keep_running = False
        return curr_dir
    elif cmd[0] == 'submit':
        keep_running = not check()

    if cmd[0] in command_list:
        curr_dir = '~' + command_list[cmd[0]](curr_dir.replace('~', 'tenv'), cmd[1:])[4:]
    return curr_dir


def check():
    with open("vulnerabilities/{}/checker.json".format(vulnerability_name)) as f:
        check_script = json.load(f)

    print('[*] Checking ...')

    groups = {}

    for step in check_script['steps']:
        print(' -  {} ... '.format(step['note']), end='')
        res = False
        if step['action'] == 'check file content':
            if os.path.exists(step['parameters']['path']):
                with open(step['parameters']['path']) as f:
                    content = ''.join(f.readlines())
                    res = (content == step['parameters']['content'])
        print(res)

        step['group'] = step.get('group', 'default')
        groups[step['group']] = groups.get(step['group'], 0) + res

    print('[*] Checking Result:')
    for group in check_script['group_check']:
        group_limit = check_script['group_check'][group]  # [min, max], close interval.
        group_res = groups.get(group, 0)
        res = (group_limit[0] <= group_res <= group_limit[1])
        if res:
            print(' -  Group \'{}\': True'.format(group))
        else:
            print(' -  Group \'{}\': False'.format(group))
            print('[*] Checking Failed.')
            return False
    print('Checking Passed.')
    checking_passed()
    return True


def checking_passed():
    print(r"""
   ____ _               _    _               ____                        _ 
  / ___| |__   ___  ___| | _(_)_ __   __ _  |  _ \ __ _ ___ ___  ___  __| |
 | |   | '_ \ / _ \/ __| |/ / | '_ \ / _` | | |_) / _` / __/ __|/ _ \/ _` |
 | |___| | | |  __/ (__|   <| | | | | (_| | |  __/ (_| \__ \__ \  __/ (_| |
  \____|_| |_|\___|\___|_|\_\_|_| |_|\__, | |_|   \__,_|___/___/\___|\__,_|
                                     |___/                                 
""")


if __name__ == '__main__':
    # cleanup tenv
    destroy_tenv()

    vulnerability_name = input("Vulnerability Name: ").lower().replace(' ', '_')
    print("Loading [{}] ...".format(vulnerability_name))
    # vulnerability_name = 'dll_hijacking'

    # load test-env config file and build the tenv.
    with open("vulnerabilities/{}/tenv.config.json".format(vulnerability_name)) as f:
        build_tenv(json.load(f))

    print('\n' * 2)
    print("=" * 10, "Vulnerability [{}] Started!".format(vulnerability_name), '=' * 10)

    # get the help file.
    with open("vulnerabilities/{}/help.json".format(vulnerability_name)) as f:
        get_help(json.load(f))

    # start hacking!
    print('-' * 10, 'START HACKING!', '-' * 10)
    keep_running = True
    curr_dir = '~'
    while keep_running:
        cmd = input("{}$ ".format(curr_dir)).split()
        # curr_dir = run_command(curr_dir, cmd)
        try:
            curr_dir = run_command(curr_dir, cmd)
        except BaseException as e:
            # pass
            print("ERROR:", e)
        print()

    destroy_tenv()
