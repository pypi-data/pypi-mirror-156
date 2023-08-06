# -*- coding: utf-8 -*-
from __future__ import annotations

from os import PathLike
from typing import Any, Protocol, TypeVar, Union, runtime_checkable

AnyStr_co = TypeVar("AnyStr_co", str, bytes, covariant=True)

FilePathType = Union[str, bytes, PathLike[str], PathLike[bytes], int]


@runtime_checkable
class Openable(Protocol):
    def open(self, *args, **kwargs) -> Any:
        ...


@runtime_checkable
class Readable(Protocol[AnyStr_co]):
    def seek(self, __offset: int, __whence: int = ...) -> int:
        # with one argument: gzip.GzipFile, bz2.BZ2File
        # with two arguments: zip.ZipFile, read_sas
        ...

    def read(self, __n: int | None = ...) -> AnyStr_co:
        # for BytesIOWrapper, gzip.GzipFile, bz2.BZ2File
        ...


@runtime_checkable
class FastApiFile(Protocol):
    file: Readable
    content_type: str
    filename: str


GeneralPath = Union[Readable, Openable, FilePathType]
GeneralPathOrUpload = Union[GeneralPath, FastApiFile]
