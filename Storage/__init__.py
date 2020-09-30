from os import path


file = path.join(path.dirname(__file__), 'Data/Users.json')
if not path.exists(file):
    with open(file, 'a') as f:
        f.write('{}')
