import os
from app.repository import init_repository
import os
import json

from app.repository import add_file

def test_init_repository(tmp_path):

    os.chdir(tmp_path)

    init_repository()

    assert os.path.exists(".sbac")
    assert os.path.exists(".sbac/commits")
    assert os.path.exists(".sbac/baselines")



def test_add_file(tmp_path):

    os.chdir(tmp_path)

    init_repository()

    with open("test.txt", "w") as f:
        f.write("hola")

    add_file("test.txt")

    with open(".sbac/tracked_files.json", "r") as f:
        tracked = json.load(f)

    assert "test.txt" in tracked

def test_add_duplicate_file(tmp_path):

    os.chdir(tmp_path)

    init_repository()

    with open("test.txt", "w") as f:
        f.write("hola")

    add_file("test.txt")
    add_file("test.txt")

    with open(".sbac/tracked_files.json", "r") as f:
        tracked = json.load(f)

    assert tracked.count("test.txt") == 1