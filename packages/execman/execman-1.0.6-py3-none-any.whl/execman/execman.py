import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List

import typer

app = typer.Typer()


class BGColor:
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


@app.command()
def execman(commands: List[Path]):
    try:
        commands = [str(command) for command in commands]
        lines = []
        is_contained_ignore = os.path.isfile('./.execmanignore')
        if is_contained_ignore:
            with open('./.execmanignore') as file:
                lines = file.readlines()
                lines = [line.rstrip() for line in lines]

        exclude = lines + ['venv', '.idea', '.git', '__pycache__', 'execman', 'lib', 'result', 'build', 'dist']

        main_folder = [str(name) for name in os.listdir(".") if
                       os.path.isdir(name) and name not in exclude]
        index = 1
        for first_level_folder in main_folder:
            os.chdir(f'./{first_level_folder}')
            for command in commands:
                os.system(command)
            print('======================================================================')
            print(f'{BGColor.OKGREEN}{datetime.now()} :: {index}.{first_level_folder} is execute', BGColor.ENDC)
            print('======================================================================')
            index = index + 1
            os.chdir('../')
        print(f'{BGColor.OKBLUE}{datetime.now()} :: finished{BGColor.ENDC}')
    except Exception as error:
        print(error)
        pass


if __name__ == '__main__':
    app()
