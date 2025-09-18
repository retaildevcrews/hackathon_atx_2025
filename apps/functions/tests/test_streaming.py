from io import BytesIO
from ..core.streaming import iter_file_chunks


def test_iter_file_chunks_within_limit():
    data = b"a" * 1024
    gen, total, digest = iter_file_chunks(BytesIO(data), 2048)
    collected = b"".join(list(gen))
    assert collected == data
    assert total == 1024
    assert len(digest) == 64


def test_iter_file_chunks_exceeds_limit():
    data = b"a" * 4096
    gen, total, digest = iter_file_chunks(BytesIO(data), 1024)
    # generator should stop early; total will reflect bytes read before noticing exceed
    parts = list(gen)
    assert total > 1024  # we only detect after reading chunk causing exceed
    # we won't use digest in this scenario further
