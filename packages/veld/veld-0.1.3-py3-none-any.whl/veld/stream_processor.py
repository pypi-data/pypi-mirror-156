# -*- coding: utf-8 -*-

"""Definitions for processing a data stream

This file is part of the Veld package.

Author: G.J.J. van den Burg
License: See the LICENSE file
Copyright: (c) 2022, G.J.J. van den Burg

"""

import sys

from typing import Iterator
from typing import List
from typing import Optional
from typing import TextIO
from typing import Union

from .exceptions import StreamProcessingError


class StreamProcessor:
    def __init__(
        self,
        path: Optional[str] = None,
        sep: str = None,
        encoding: str = "utf-8",
        flatten: bool = False,
        ignore_invalid: bool = False,
    ):
        self._path = path
        self._sep = sep
        self._ignore_invalid = ignore_invalid
        self._encoding = encoding
        self._flatten = flatten

        self._stream = None  # type: Optional[TextIO]
        self._stream_iter = None  # type: Optional[Iterator[List[float]]]
        self._last_line = None  # type: Optional[str]

    @property
    def stream(self) -> TextIO:
        """Return the stream that we're reading from"""
        if not self._stream is None:
            return self._stream
        if self._path is None:
            self._stream = sys.stdin
        else:
            self._stream = open(self._path, "r", encoding=self._encoding)
        return self._stream

    @property
    def last_line(self) -> Optional[str]:
        """The most recently parsed line"""
        return self._last_line

    def close_stream(self):
        if self._stream is None:
            return
        if self._stream == sys.stdin:
            return
        self._stream.close()

    def __iter__(self) -> "StreamProcessor":
        self._stream_iter = self.process_stream()
        return self

    def __next__(self) -> List[float]:
        assert not self._stream_iter is None
        return next(self._stream_iter)

    def process_stream(self) -> Iterator[List[float]]:
        """Process the input stream"""
        for line in self.stream:
            self._last_line = line

            # Skip empty lines
            if not line.strip():
                continue

            # Split the line in case of multidimensional data
            parts = line.split(sep=self._sep)

            # Parse numbers from text
            values = list(map(self.parse_numeric, parts))

            # Flatten the input array if desired
            if self._flatten:
                for value in values:
                    yield [value]
            else:
                yield values
        self.close_stream()

    def parse_numeric(self, x: str) -> float:
        """Parse a string number, preserving type"""
        x = x.rstrip("\r\n")
        parse_func = float if "." in x else int
        try:
            return parse_func(x)
        except ValueError:
            pass
        if self._ignore_invalid:
            return float("nan")
        self.close_stream()
        raise StreamProcessingError(x)
