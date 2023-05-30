import os


def listdir(d: str):
    return os.listdir(d)


def path_join(d, p):
    last_name = p.split('/')[-1]
    cd_path = '/'.join(p.split('/')[:-1])
    cd_path = cd(d, ['/' + cd_path if p[0] == '/' else cd_path])
    path = cd_path + '/' + last_name
    folder_path = path if os.path.isdir(path) else cd_path
    return path, folder_path


class FileSystem:
    def __init__(self):
        self.root = {
            'type': 'folder',
            'body': {}
        }
        self.current_dir_path = '~'
        self.current_dir = self.root
        self.authority = {
            id(self.root): 'rwx'
        }

    def listdir(self, d):
        return list(self.current_dir['body'].keys())

    def isdir(self, d):
        return True

    def __getitem__(self, path):
        if path == '~' or path == '':
            return self.root
        path = path[2:].strip('/').split('/')
        d = self.root
        for name in path:
            if name in d['body'].keys():
                d = d['body'][name]
            else:
                print('No such file or directory')
                raise Exception('Error 0x002')
        return d

    def set_authority(self, name, authority):
        self.authority[id(self[name])] = authority

    def get_authority(self, name):
        return self.authority[id(self[name])]

    def have_authority(self, target_dir: str, permissions: str):
        # backup
        backup_curr_dir_path = self.current_dir_path
        backup_curr_dir = self.current_dir

        # get authority
        index = id(self[target_dir])
        authority = self.authority[index]

        # restore
        self.current_dir_path = backup_curr_dir_path
        self.current_dir = backup_curr_dir

        return all(p in authority for p in permissions)

    def cd(self, new_dir: str):
        d = self.current_dir_path[2:]  # remove '~/' from path

        def helper():
            nonlocal d, new_dir

            while '//' in new_dir:
                new_dir = new_dir.replace('//', '/')

            if not self.have_authority(d, 'r'):
                print("Permission denied")
                raise Exception('Error 0x003')
            if new_dir == '..':
                d = d.split('/')
                d.pop()
                if d:
                    return '/'.join(d)
                else:
                    return ''
            if new_dir[0] == '/':
                return new_dir[1:]
            elif '/' in new_dir:
                for name in new_dir.split('/'):
                    d += self.cd(name)
                return d
            elif new_dir in self.listdir(d) and self.isdir(d + '/' + new_dir):
                return d + '/' + new_dir
            else:
                print('No such file or directory')
                raise Exception('Error 0x002')

        res = helper()
        while '//' in res:
            res = res.replace('//', '/')
        res = '~/' + res.strip('/')  # prevent paths like '~/'

        self.current_dir_path = res
        self.current_dir = self[res]

    def mkdir(self, new_dir: str):
        self.current_dir['body'][new_dir] = {
            'type': 'folder',
            'body': {}
        }
        self.set_authority(self.current_dir_path + '/' +
                           new_dir, self.get_authority(self.current_dir_path))


class File:
    def __init__(self, content: str):
        self.content = content

    @classmethod
    def load(cls, path: str):
        with open(path, 'r') as f:
            content = f.read()
        return cls(content)

    def __getitem__(self, item):
        if item == 'content':
            return self.content
        elif item == 'type':
            return 'file'

    def read(self):
        return self.content

    def write(self, content: str):
        self.content = content


if __name__ == '__main__':
    fs = FileSystem()
    while 1:
        print(eval(input(">>> ")))
