# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
from contextlib import contextmanager
from functools import wraps
from typing import Generator, Optional

from .types import FilePathType, Openable, Readable

_LOG = logging.getLogger(__name__)


def catch_exceptions(func, exceptions):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except exceptions:
            return None

    return wrapper


def frame_chunker(frame, chunk_size):
    for i in range(0, len(frame), chunk_size):
        yield frame.iloc[i : (i + chunk_size)]


class PandasLoader:
    def __getattr__(self, item):
        try:
            import pandas  # type: ignore # pylint: disable=import-outside-toplevel
        except ImportError:
            raise ImportError(f"pandas.{item} is not available, pandas is not installed") from None
        return getattr(pandas, item)


pd = PandasLoader()


@contextmanager
def lazy_open(
    file: Readable | Openable | FilePathType,
    *args,
    **kwargs,
) -> Generator[Readable, None, None]:
    if isinstance(file, Readable):
        file.seek(0)
        try:
            yield file
        finally:
            file.seek(0)
    elif isinstance(file, Openable):
        with file.open(*args, **kwargs) as fh:
            yield fh
    else:
        with open(file, *args, **kwargs) as fh:  # pylint: disable=unspecified-encoding
            yield fh


class LazyOpener:
    def __init__(
        self,
        file: Readable | Openable | FilePathType,
        *args,
        **kwargs,
    ):
        self._fh: Readable
        self.file = file
        self.args = args
        self.kwargs = kwargs
        self._closed: Optional[bool] = None

    def open(self) -> Readable:
        self._closed = False
        if isinstance(self.file, Readable):
            self.file.seek(0)
            return self.file
        if isinstance(self.file, Openable):
            self._fh = self.file.open(*self.args, **self.kwargs)
        else:
            self._fh = open(  # pylint: disable=unspecified-encoding,consider-using-with
                self.file, *self.args, **self.kwargs
            )
        return self._fh

    def close(self):
        if self._closed:
            return
        if isinstance(self.file, Readable):
            self.file.seek(0)
        else:
            try:
                self._fh.close()
            except Exception as e:  # pylint: disable=broad-except
                _LOG.warning("Error closing file %s: %s", self.file, e)

    def __enter__(self):
        return self.open()

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.close()

    def __del__(self):
        self.close()
