from pathlib import Path

def get_file(filename):
    """
    opens a url
    """
    if not Path(filename).is_file():
        return None
    return open(filename, "rb")
