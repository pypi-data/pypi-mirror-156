"""
    ulid/codec
    ~~~~~~~~~~

    Defines encoding/decoding functions for SerialId data representations.
"""
import datetime
import typing

from . import hints, base32, serialid

#: Type hint that defines multiple primitive types that can represent
#: a Unix timestamp in seconds.
TimestampPrimitive = typing.Union[hints.Primitive,  # pylint: disable=invalid-name
                                  datetime.datetime, serialid.Timestamp, serialid.SerialId]


#: Type hint that defines multiple primitive types that can represent randomness.
RandomnessPrimitive = typing.Union[hints.Primitive, serialid.Randomness, serialid.SerialId]  # pylint: disable=invalid-name


def decode_timestamp(timestamp: TimestampPrimitive) -> serialid.Timestamp:
    """
    Create a new :class:`~serialid.serialid.SerialId` instance using a timestamp value of a supported type.

    The following types are supported for timestamp values:

    * :class:`~datetime.datetime`
    * :class:`~int`
    * :class:`~float`
    * :class:`~str`
    * :class:`~memoryview`
    * :class:`~serialid.serialid.Timestamp`
    * :class:`~serialid.serialid.SerialId`
    * :class:`~bytes`
    * :class:`~bytearray`

    :param timestamp: Unix timestamp in seconds
    :type timestamp: See docstring for types
    :return: SerialId using given timestamp and new randomness
    :rtype: :class:`~serialid.serialid.SerialId`
    :raises ValueError: when the value is an unsupported type
    :raises ValueError: when the value is a string and cannot be Base32 decoded
    :raises ValueError: when the value is or was converted to something 48 bits
    """
    if isinstance(timestamp, datetime.datetime):
        timestamp = int(timestamp.timestamp() * 100).to_bytes(5, byteorder='big')
    if isinstance(timestamp, (int, float)):
        timestamp = int(timestamp * 100.0).to_bytes(5, byteorder='big')
    elif isinstance(timestamp, str):
        timestamp = base32.decode_segment(timestamp[:8])
    elif isinstance(timestamp, memoryview):
        timestamp = timestamp.tobytes()
    elif isinstance(timestamp, serialid.Timestamp):
        timestamp = timestamp.bytes
    elif isinstance(timestamp, serialid.SerialId):
        timestamp = timestamp.timestamp().bytes

    if not isinstance(timestamp, (bytes, bytearray)):
        raise ValueError('Expected datetime, int, float, str, memoryview, Timestamp, SerialId, '
                         'bytes, or bytearray; got {}'.format(type(timestamp).__name__))

    length = len(timestamp)
    if length != 5:
        raise ValueError('Expects timestamp to be 40 bits; got {} bytes'.format(length))

    return serialid.Timestamp(timestamp)


def decode_randomness(randomness: RandomnessPrimitive) -> serialid.Randomness:
    """
    Create a new :class:`~serialid.serialid.Randomness` instance using the given randomness value of a supported type.

    The following types are supported for randomness values:

    * :class:`~int`
    * :class:`~float`
    * :class:`~str`
    * :class:`~memoryview`
    * :class:`~serialid.serialid.Randomness`
    * :class:`~serialid.serialid.SerialId`
    * :class:`~bytes`
    * :class:`~bytearray`

    :param randomness: Random bytes
    :type randomness: See docstring for types
    :return: SerialId using new timestamp and given randomness
    :rtype: :class:`~serialid.serialid.SerialId`
    :raises ValueError: when the value is an unsupported type
    :raises ValueError: when the value is a string and cannot be Base32 decoded
    :raises ValueError: when the value is or was converted to something 80 bits
    """
    if isinstance(randomness, (int, float)):
        randomness = int(randomness).to_bytes(5, byteorder='big')
    elif isinstance(randomness, str):
        if len(randomness) == 8:
            randomness = base32.decode_segment(randomness)
        elif len(randomness) == 16 or len(randomness) == 17:
            randomness = base32.decode_segment(randomness[-8:])
    elif isinstance(randomness, memoryview):
        randomness = randomness.tobytes()
    elif isinstance(randomness, serialid.Randomness):
        randomness = randomness.bytes
    elif isinstance(randomness, serialid.SerialId):
        randomness = randomness.randomness().bytes

    if not isinstance(randomness, (bytes, bytearray)):
        raise ValueError('Expected int, float, str, memoryview, Randomness, SerialId, '
                         'bytes, or bytearray; got {}'.format(type(randomness).__name__))

    length = len(randomness)
    if length != 5:
        raise ValueError('Expects randomness to be 40 bits; got {} bytes'.format(length))

    return serialid.Randomness(randomness)
