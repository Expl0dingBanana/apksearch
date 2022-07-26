import os


def get_test_contents(filename):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(dir_path, "web_results", filename)
    with open(path, "rb") as fh:
        return fh.read()
