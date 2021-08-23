from loguru import logger as _logger
from tqdm import tqdm

_logger.remove()
_logger.add(lambda text: tqdm.write(text, end=""), colorize=True, enqueue=True)

logger = _logger
