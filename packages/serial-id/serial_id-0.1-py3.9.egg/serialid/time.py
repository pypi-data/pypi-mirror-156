"""
    serialid/time
    ~~~~~~~~~

    Contains functionality for current time providers.
"""
import abc
import sys
import time

from . import hints


__all__ = ['Provider', 'DEFAULT', 'centiseconds', 'milliseconds', 'microseconds']


class Provider(metaclass=abc.ABCMeta):
    """
    Abstract class that defines providers for current time values.
    """
    abc.abstractmethod
    def centiseconds(self) -> hints.Int:
        """
        Get the current time since unix epoch in centiseconds.

        :return: Epoch timestamp in centiseconds.
        :rtype: :class:`~int`
        """
        raise NotImplementedError('Method must be implemented by derived class')

    @abc.abstractmethod
    def milliseconds(self) -> hints.Int:
        """
        Get the current time since unix epoch in milliseconds.

        :return: Epoch timestamp in milliseconds.
        :rtype: :class:`~int`
        """
        raise NotImplementedError('Method must be implemented by derived class')

    @abc.abstractmethod
    def microseconds(self) -> hints.Int:
        """
        Get the current time since unix epoch in microseconds.

        :return: Epoch timestamp in microseconds.
        :rtype: :class:`~int`
        """
        raise NotImplementedError('Method must be implemented by derived class')


class DefaultProvider(Provider):
    """
    Returns time values from :func:`~time.time`.
    """
    def centiseconds(self) -> hints.Int:
        """
        Get the current time since unix epoch in centiseconds.

        :return: Epoch timestamp in centiseconds.
        :rtype: :class:`~int`
        """
        return int(time.time() * 100)

    def milliseconds(self) -> hints.Int:
        """
        Get the current time since unix epoch in milliseconds.

        :return: Epoch timestamp in milliseconds.
        :rtype: :class:`~int`
        """
        return int(time.time() * 1000)

    def microseconds(self) -> hints.Int:
        """
        Get the current time since unix epoch in microseconds.

        :return: Epoch timestamp in microseconds.
        :rtype: :class:`~int`
        """
        return int(time.time() * 1000 * 1000)


class NanoProvider(Provider):
    """
    Returns time values from :func:`~time.time_ns`.

    This class will only work on python 3.7+.
    """
    def centiseconds(self) -> hints.Int:
        """
        Get the current time since unix epoch in centiseconds.

        :return: Epoch timestamp in centiseconds.
        :rtype: :class:`~int`
        """
        return time.time_ns() // 10000000

    def milliseconds(self) -> hints.Int:
        """
        Get the current time since unix epoch in milliseconds.

        :return: Epoch timestamp in milliseconds.
        :rtype: :class:`~int`
        """
        return time.time_ns() // 1000000

    def microseconds(self) -> hints.Int:
        """
        Get the current time since unix epoch in microseconds.

        :return: Epoch timestamp in microseconds.
        :rtype: :class:`~int`
        """
        return time.time_ns() // 1000


if sys.version_info >= (3, 7):
    DEFAULT = NanoProvider()
else:
    DEFAULT = DefaultProvider()

centiseconds = DEFAULT.centiseconds
milliseconds = DEFAULT.milliseconds
microseconds = DEFAULT.microseconds

