import os


def listdir(d: str):
    return os.listdir(d)


class FileSystem:
    def __init__(self):
        self.root = {}


class File:
    def __init__(self, path: str, authority: str = 'rwx'):
        with open(path, 'r') as f:
            self.content = f.read()
        self.authority = authority

    def read(self):
        return self.content

    def write(self, content: str):
        self.content = content
