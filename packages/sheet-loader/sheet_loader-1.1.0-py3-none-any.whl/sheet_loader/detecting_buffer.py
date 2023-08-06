# -*- coding: utf-8 -*-
from __future__ import annotations

import logging
from collections import deque
from csv import Sniffer
from multiprocessing import Pipe, Process
from multiprocessing.connection import Connection
from typing import Optional

from chardet import UniversalDetector

from .helpers import LazyOpener, catch_exceptions
from .types import FilePathType, Openable, Readable

_LOG = logging.getLogger(__name__)
CHUNK_SIZE = 32 * 1024  # 128 kb chunks
MAGIC_BYTE_SEQUENCE = b"\xde\xca\xf0\xde\xad\xbe\xef"
MAX_DETECTION_SIZE = 1 * 1024 * 1024  # 1MB max detection size
DEFAULT_START_ENCODING = "utf-8"
ENCODING_PREFIX_LENGTH = 16
CSV_SAMPLE_SIZE = 512 * 1024  # 512 kb sample size


class DetectingBuffer(Readable):
    def seek(self, __offset: int, __whence: int = ...) -> int:
        raise NotImplementedError

    def __init__(
        self,
        file: Readable | Openable | FilePathType,
        newline=None,
        **kwargs,
    ) -> None:
        super().__init__()

        self._newline = newline
        kwargs["mode"] = "rb"
        self._opener = LazyOpener(file, **kwargs)
        self._open_file = self._opener.open()
        self._in_read, self._in_write = Pipe(duplex=False)
        self._out_read, self._out_write = Pipe(duplex=False)
        self._reader = Process(
            target=self.reader,
            kwargs={
                "file": self._open_file,
                "in_writer": self._in_write,
                "chunk_size": kwargs.get("chunk_size", CHUNK_SIZE),
            },
            daemon=True,
        )

        self._processor = Processor(in_reader=self._in_read, out_writer=self._out_write)
        self._reader.start()
        self._processor.start()
        self._buffer: deque = deque()
        self._done = False
        self._leftovers = ""
        self._closed = False

    @staticmethod
    def reader(file, in_writer: Connection, chunk_size=CHUNK_SIZE):
        while chunk := file.read(chunk_size):
            in_writer.send_bytes(chunk)
        in_writer.send_bytes(MAGIC_BYTE_SEQUENCE)
        in_writer.close()

    # noinspection PyMethodMayBeStatic
    def seekable(self) -> bool:
        return False

    def _fetch_chunk(self):
        if self._done:
            return ""
        try:
            chunk = self._out_read.recv()
        except EOFError:
            self._done_reading()
            return ""
        if chunk == MAGIC_BYTE_SEQUENCE:
            self._done_reading()
            return ""
        if self._newline is None:
            chunk = chunk.replace("\r\n", "\n")
            chunk = chunk.replace("\r", "\n")
        return chunk

    def _done_reading(self):
        if self._closed:
            return
        catch_exceptions(self._out_read.close, [OSError])()
        catch_exceptions(self._out_write.close, [OSError])()
        catch_exceptions(self._in_read.close, [OSError])()
        catch_exceptions(self._in_write.close, [OSError])()
        self._reader.join()
        self._processor.join()

        self._done = True
        self._opener.close()
        self._closed = True

    def __del__(self):
        self._done_reading()

    def peek(self, size: int | None = None) -> str:
        out = self.read(size)
        self._leftovers = out + self._leftovers
        return out

    def read(self, size: int | None = None) -> str:
        output = ""
        size = size or -1
        if size < 0:
            if self._leftovers:
                output += self._leftovers
                self._leftovers = ""
            while chunk := self._fetch_chunk():
                output += chunk
            return output
        while size > 0:
            if self._leftovers:
                nc = self._leftovers[:size]
                self._leftovers = self._leftovers[size:]
                output += nc
                size -= len(nc)
                continue
            chunk = self._fetch_chunk()
            if chunk == "":
                break
            if len(chunk) > size:
                self._leftovers = chunk[size:]
                output += chunk[:size]
                break

            output += chunk
            size -= len(chunk)

        return output

    def readline(self):
        str_buf = self.read(1024)
        if self._newline is None:
            nl = "\n"
        else:
            nl = self._newline
        while nl not in str_buf:
            r = self.read(1024)
            str_buf += r
            if r == "":
                break
        if nl in str_buf:
            ret = str_buf[: str_buf.index(nl) + 1]
            self._leftovers = str_buf[len(ret) :] + self._leftovers
        else:
            ret = str_buf
        return ret

    def __next__(self):
        r = self.readline()
        if r == "":
            raise StopIteration
        return r

    def __iter__(self):
        return self

    def get_csv_dialect(
        self,
        sniffer: Optional[Sniffer] = None,
        delimiters: Optional[str] = None,
        sample_size=CSV_SAMPLE_SIZE,
    ):
        sniffer = sniffer or Sniffer()
        buffer = self.read(sample_size)
        dialect = sniffer.sniff(buffer, delimiters=delimiters)
        self._leftovers = buffer + self._leftovers
        return dialect


class Processor(Process):
    def __init__(self, in_reader: Connection, out_writer: Connection):
        super().__init__(name="Processor", daemon=True)
        self._in_reader = in_reader
        self._out_writer = out_writer
        self._total_bytes = 0
        self._detector = UniversalDetector()
        self.current_enc = DEFAULT_START_ENCODING
        self.last_encodings: deque = deque(maxlen=3)
        self.result = None
        self._stop_feeding = False

    def feed_detector(self, chunk):
        self._detector.feed(chunk)

        self.result = self.get_best_encoding()
        if self.result["encoding"] is not None:
            self.last_encodings.append(self.current_enc)
            self.current_enc = self.result["encoding"]
            if set(self.last_encodings) == {self.current_enc}:
                self._stop_feeding = True
        self._out_writer.send(chunk.decode(self.current_enc))

    def get_best_encoding(self):
        dd = self._detector.done
        result = self._detector.close()
        self._detector.done = dd
        return result

    def feed_and_process(self, chunk):
        if self._stop_feeding or self._detector.done or self._total_bytes > MAX_DETECTION_SIZE:
            # no more detection needed (at least for now)
            try:
                self._out_writer.send(chunk.decode(self.current_enc))
            except UnicodeError:
                _LOG.debug(
                    'Could not decode chunk with encoding "%s", re-feeding', self.current_enc
                )
                self.feed_detector(chunk)
        else:
            self.feed_detector(chunk)

    def run(self):
        chunk = b""
        while True:
            try:
                nc = self._in_reader.recv_bytes()
            except EOFError:
                nc = b""
            if nc == MAGIC_BYTE_SEQUENCE:
                nc = b""
            chunk += nc

            if chunk == b"":
                # empty chunk means we're done
                break
            if nc and (nc[-1] > 0x7F or nc[-1] in (ord("\n"), ord("\r"))):
                # last byte is not ascii, or last byte is some type of line ending,
                # let's get some more, so we don't split a character
                continue
            self.feed_and_process(chunk)
            self._total_bytes += len(chunk)
            chunk = b""
            if nc == b"":
                # empty next chunk means done
                break
        self._out_writer.send(MAGIC_BYTE_SEQUENCE)
        catch_exceptions(self._in_reader.close, [OSError])()
        catch_exceptions(self._out_writer.close, [OSError])()
