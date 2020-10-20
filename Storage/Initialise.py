from os import path
import os

if __name__ == "__main__":
    file = path.join(f'{os.getenv("DATA_FOLDER")}/Users.json')
    print(file)
    if not path.exists(file):
        with open(file, 'a') as f:
            f.write('{}')
