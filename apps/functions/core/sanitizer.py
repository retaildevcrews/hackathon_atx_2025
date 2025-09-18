import re

_filename_re = re.compile(r"[^A-Za-z0-9._-]+")

def sanitize_filename(name: str) -> str:
    name = name.strip()
    # remove path components if any
    name = name.split("/")[-1].split("\\")[-1]
    name = _filename_re.sub("_", name)
    if not name:
        return "file"
    return name[:120]
