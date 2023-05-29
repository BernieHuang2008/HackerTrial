import os
import shutil
import filesystem as fs


def ls(d, args):
    if not have_permission(d, 'r'):
        print("Permission denied")
        raise Exception('Error 0x003')
    if args:
        lst = fs.listdir(cd(d, args))
    else:
        lst = fs.listdir(d)
    if '.config' in lst:
        lst.remove('.config')
    print('\n'.join(lst))
    return d


def cd(d, args):
    if not args or not args[0]:
        return d

    def helper():
        nonlocal d, args
        args[0] = args[0].replace('//', '/')
        if not have_permission(d, 'r'):
            print("Permission denied")
            raise Exception('Error 0x003')
        if args[0] == '..':
            d = d.split('/')
            d.pop()
            if d:
                return '/'.join(d)
            else:
                return 'tenv'
        if args[0][0] == '/':
            return "tenv" + args[0]
        elif args[0].count('/') > 0:
            for name in args[0].split('/'):
                d = cd(d, [name])
            return d
        elif args[0] in fs.listdir(d) and os.path.isdir(d + '/' + args[0]):
            return d + '/' + args[0]
        else:
            print('No such file or directory')
            raise Exception('Error 0x002')

    res = helper()
    res = res.replace('//', '/').strip('/')
    return res


def pathjoin(d, p):
    last_name = p.split('/')[-1]
    cd_path = '/'.join(p.split('/')[:-1])
    cd_path = cd(d, ['/' + cd_path if p[0] == '/' else cd_path])
    path = cd_path + '/' + last_name
    folder_path = path if os.path.isdir(path) else cd_path
    return path, folder_path


def mv(d, args):
    if len(args) != 2:
        print("No enough arguments")
        raise Exception('Error 0x004')

    src, src_path = pathjoin(d, args[0])
    des, des_path = pathjoin(d, args[1])

    if not have_permission(src_path, 'rw') or not have_permission(des_path, 'w'):
        print("Permission denied")
        raise Exception('Error 0x003')

    shutil.move(src, des)
    return d


def copy(d, args):
    if len(args) != 2:
        print("No enough arguments")
        raise Exception('Error 0x004')

    src, src_path = pathjoin(d, args[0])
    des, des_path = pathjoin(d, args[1])

    if not have_permission(src_path, 'r') or not have_permission(des_path, 'w'):
        print("Permission denied")
        raise Exception('Error 0x003')

    shutil.copy(src, des)
    return d


def have_permission(d, permissions):
    with open(d + "/.config") as f:
        flags = f.readline().strip()
    return all(p in flags for p in permissions)


def cat(d, args):
    if not args:
        print('No enough arguments')
        raise Exception('Error 0x004')
    path, folder_path = pathjoin(d, args[0])
    if os.path.isfile(path):
        with open(path, 'r') as f:
            print(''.join(f.readlines()))
    else:
        print('Invalid arguments')
        raise Exception('Error 0x005')


command_list = {
    'ls': ls,
    'cd': cd,
    'mv': mv,
    'copy': copy,
    'cat': cat,
}

