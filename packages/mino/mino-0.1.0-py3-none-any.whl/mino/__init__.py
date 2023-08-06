import os
import sys

from mino.mino import convert_schema_in_file

def convert():
    cwd = os.getcwd()
    relative_path = sys.argv[1]
    file_path =  os.path.join(cwd, relative_path)
    print(convert_schema_in_file(file_path))
