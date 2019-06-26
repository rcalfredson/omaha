"""Helper functions for disk I/O (write, read, delete).
"""
import glob
import json
import os

def glob_delete(path, glob_pattern, file_to_keep=''):
    """
    Deletes all files on the specified relative path that match the supplied glob pattern,
    excluding (optionally) a filename that would otherwise have been matched and deleted.

    Arguments:
      - path: the path on which to look for files; should be given relative to the /lib
              directory (e.g. ../data/alphavantage).
      - glob_pattern: the glob pattern for which matching files will be deleted.
      - file_to_keep (optional): name of a file not to delete, even if it would have been
                                 matched by the glob pattern.
    """
    dirname = os.path.dirname(__file__)
    file_to_keep = os.path.join(dirname, path, file_to_keep)
    files = glob.glob(os.path.join(dirname, path, glob_pattern))
    for file in files:
        if file != file_to_keep:
            os.remove(file)

def write(filename, data):
    """
    Writes an object to the specified file as JSON.

    Arguments:
      - filename: the name of the file to which to write, with a path attached that is
                  relative to the /lib directory (e.g. ../data/alphavantage/filename.json).
      - data: the object to write to the file.
    """
    with open(os.path.join(os.path.dirname(__file__), filename), 'w') as outfile:
        json.dump(data, outfile)

def json_from_file(filename):
    """
    Loads a Python object from a JSON file.

    Arguments:
      - filename: the name of the file to read, with a path attached that is relative to
                  the /lib directory (e.g. ../data/alphavantage/filename.json).
    """
    with open(os.path.join(os.path.dirname(__file__), filename)) as json_file:
        return json.load(json_file)
    