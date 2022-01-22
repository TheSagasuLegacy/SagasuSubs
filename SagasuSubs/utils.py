import hashlib
import os
from asyncio import AbstractEventLoop, Future, Semaphore, wait_for
from pathlib import Path
from typing import Callable, Iterator, Optional, TypeVar

import cchardet

T_Wrapped = TypeVar("T_Wrapped", bound=Callable)


def overrides(InterfaceClass: object):
    def overrider(func: T_Wrapped) -> T_Wrapped:
        assert func.__name__ in dir(InterfaceClass), f"Error method: {func.__name__}"
        return func

    return overrider


class AdvanceSemaphore(Semaphore):
    _loop: AbstractEventLoop
    _finshed_future: Optional[Future]

    def __init__(self, value: int) -> None:
        super().__init__(value=value)
        self._initial_value = value
        self._finshed_future = None

    def _check_value(self) -> None:
        if (
            (self._value >= self._initial_value)
            and (not self._waiters)
            and (self._finshed_future is not None)
            and (not self._finshed_future.done())
        ):
            self._finshed_future.set_result(None)

    def release(self) -> None:
        super().release()
        self._check_value()

    async def wait_all_finish(self, timeout: float = None):
        self._finshed_future = self._loop.create_future()
        self._check_value()
        await wait_for(self._finshed_future, timeout)


def sha1sum(file: Path) -> str:
    """
    Calculate the sha1 hash of a file.
    """
    return hashlib.sha1(file.read_bytes()).hexdigest()


def detect_encoding(file: Path) -> Optional[str]:
    """
    Detect file encoding using cchardet
    """
    with file.open("rb") as f:
        return cchardet.detect(f.read())["encoding"]


def iterate_files(directory: Path, ext: str = None) -> Iterator[Path]:
    """
    Walk path and return file paths with specified extension name.
    """
    for dir, folders, files in os.walk(directory):
        for file in files:
            if ext and not file.endswith(ext):
                continue
            yield Path(dir) / file
    return


def auto_load(file: Path) -> str:
    """
    Load file using cchardet and automatically detect encoding.
    """
    with file.open(
        "r", encoding=detect_encoding(file) or "utf-8", errors="ignore"
    ) as f:
        return f.read()
