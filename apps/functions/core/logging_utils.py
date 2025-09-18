import logging

_LOGGER = None

def get_logger(level: str = "INFO"):
    global _LOGGER
    if _LOGGER is None:
        logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO), format="%(asctime)s %(levelname)s %(message)s")
        _LOGGER = logging.getLogger("guf")
    return _LOGGER
