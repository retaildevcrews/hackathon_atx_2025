from ..core.sanitizer import sanitize_filename

def test_sanitize_basic():
    assert sanitize_filename('test.pdf') == 'test.pdf'

def test_strip_paths():
    assert sanitize_filename('../../etc/passwd') == 'passwd'


def test_invalid_chars():
    out = sanitize_filename('weird name!*&^%.txt')
    assert out.startswith('weird_name') and out.endswith('.txt')
