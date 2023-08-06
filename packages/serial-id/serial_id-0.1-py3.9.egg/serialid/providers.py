import os
import typing

from . import hints
from . import time

TimestampRandomnessBytes = typing.Tuple[hints.Bytes, hints.Bytes]  # pylint: disable=invalid-name


class Provider:
    """
    Provider that creates new randomness values for the same timestamp.
    """
    def new(self) -> TimestampRandomnessBytes:
        """
        Create a new timestamp and randomness value.

        :return: Two item tuple containing timestamp and randomness values as :class:`~bytes`.
        :rtype: :class:`~tuple`
        """
        timestamp = self.timestamp()
        randomness = self.randomness(timestamp)
        return timestamp, randomness

    def timestamp(self) -> hints.Bytes:
        """
        Create a new timestamp value in centiseconds.

        :return: Timestamp value in bytes.
        :rtype: :class:`~bytes`
        """
        return (time.centiseconds()).to_bytes(5, byteorder='big')

    def randomness(self, timestamp: hints.Bytes) -> hints.Bytes:
        """
        Create a new randomness value.

        :param timestamp: Timestamp in centiseconds
        :type timestamp: :class:`~bytes`
        :return: Randomness value in bytes.
        :rtype: :class:`~bytes`
        """
        return os.urandom(5)


DEFAULT = Provider()
