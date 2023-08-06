# -*- coding: utf-8 -*-
from __future__ import annotations

import csv
import inspect
import logging
from collections import abc
from contextlib import contextmanager
from enum import Enum, auto
from pathlib import PurePath
from typing import Any, Union

from .detecting_buffer import DetectingBuffer
from .helpers import LazyOpener, frame_chunker, pd
from .types import FastApiFile, FilePathType, GeneralPath

_LOG = logging.getLogger(__name__)

_csv_sniff = csv.Sniffer()
_csv_sniff.preferred = ["|", ",", "\t"]


class SheetFileType(Enum):
    CSV = auto()
    XLS = auto()


def clean_kwargs(function, kwargs: dict):
    try:
        sig = inspect.signature(function)
        if any(v.kind == inspect.Parameter.VAR_KEYWORD for v in sig.parameters.values()):
            # variable keywords allowed, return all
            return kwargs
        return {k: v for k, v in kwargs.items() if k in sig.parameters}
    except ValueError:
        # failsafe, return all
        return kwargs


class SheetLoader(abc.Iterable):
    # pylint: disable=too-many-instance-attributes
    def __iter__(self):
        return self

    _data: Union[None, Any]
    _file_data: Union[None, LazyOpener]
    _file: GeneralPath
    _type: SheetFileType

    def __init__(self, file: FilePathType | FastApiFile, **kwargs):
        self._chunker = None
        self._all_chunks_returned = False
        self._data = None
        self._file_data = None
        self.kwargs = kwargs
        self._cur_row = 0
        if isinstance(file, FastApiFile):
            self._file = file.file
            if (
                file.content_type
                == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                or file.filename.lower().startswith(".xls")
            ):
                self._type = SheetFileType.XLS
            else:
                self._type = SheetFileType.CSV
        else:
            self._file = file
            if hasattr(file, "suffix"):
                suffix = file.suffix  # type: ignore
            else:
                suffix = PurePath(str(file)).suffix
            if suffix.lower().startswith(".xls"):
                self._type = SheetFileType.XLS
            else:
                self._type = SheetFileType.CSV

    def load_xlsx(self, **pd_kwargs):
        if hasattr(self._file, "as_uri"):
            file = self._file.as_uri()
        else:
            file = self._file
        kwargs = {"dtype": "string"}
        kwargs.update(pd_kwargs)
        kwargs = clean_kwargs(pd.read_excel, kwargs)
        self._data = pd.read_excel(file.as_uri(), **kwargs)

    def get_file_data(self, **kwargs):
        if self._file_data is None:
            self._file_data = LazyOpener(self._file, **kwargs)
        return self._file_data.open()

    def close(self):
        if self._file_data is not None:
            self._file_data.close()

    def __del__(self):
        self.close()

    @contextmanager
    def load_csv(self, csv_read_func=None, **pd_kwargs):
        if csv_read_func is None:
            csv_read_func = pd.read_csv

        db = DetectingBuffer(self._file)
        dialect = db.get_csv_dialect(sniffer=_csv_sniff)
        _LOG.debug(
            "Dialect: %s",
            {k: v for k, v in dialect.__dict__.items() if not k.startswith("_")},
        )
        preview = db.peek(1024 * 256)
        try:

            # header_line = next(
            #     csv.reader(io.StringIO(buffer, newline=None), dialect=dialect)
            # )
            # dtypes = {k: v for k, v in DTYPE_MAP.items() if k in header_line}
            # date_dtypes = [v for v in DTYPE_DATES if v in header_line]
            read_kwargs = {
                "dialect": dialect,
                "on_bad_lines": "warn",
                "dtype": "string",
                "header": 0,
            }
            read_kwargs.update(pd_kwargs)
            read_kwargs = clean_kwargs(csv_read_func, read_kwargs)
            self._data = csv_read_func(db, **read_kwargs)
        except Exception:
            _LOG.exception(preview, stack_info=True)
            raise

    def _open(self):
        if self._type == SheetFileType.CSV:
            self.load_csv(**self.kwargs)
        elif self._type == SheetFileType.XLS:
            self.load_xlsx(**self.kwargs)

    @property
    def data(self):
        if self._data is None:
            self._open()
        return self._data

    def __next__(self):
        if self._all_chunks_returned:
            raise StopIteration
        if "chunksize" not in self.kwargs:
            self._all_chunks_returned = True
            return self.data
        if self._chunker is None:
            if self._type == SheetFileType.XLS:
                self._chunker = frame_chunker(self.data, self.kwargs["chunksize"])
            else:
                self._chunker = self.data
        try:
            return next(self._chunker)
        except StopIteration:
            self._all_chunks_returned = True
            raise

    def read(self):
        if "chunksize" in self.kwargs and self._type == SheetFileType.XLS:
            return frame_chunker(self.data, self.kwargs["chunksize"])
        return self.data


def read_sheet(file: FilePathType | FastApiFile, **kwargs):
    sl = SheetLoader(file, **kwargs)
    if "chunksize" not in kwargs:
        return sl.data
    return sl
