from hashlib import sha256
from typing import Iterable, Tuple

CHUNK_SIZE = 256 * 1024  # 256KB

def iter_file_chunks(file_obj, max_bytes: int) -> Tuple[Iterable[bytes], int, str]:
    total = 0
    hasher = sha256()

    def gen():
        nonlocal total
        while True:
            chunk = file_obj.read(CHUNK_SIZE)
            if not chunk:
                break
            total += len(chunk)
            if total > max_bytes:
                # Stop yielding further
                break
            hasher.update(chunk)
            yield chunk
    return gen(), total, hasher.hexdigest()
