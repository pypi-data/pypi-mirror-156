"""
    serialid/base32
    ~~~~~~~~~~~

    Functionality for encoding/decoding SerialId strings/bytes using Base32 format.

    * `Base32 Documentation <http://www.crockford.com/wrmg/base32.html>`
"""
import array

from . import hints

#: Base32 character set. Excludes characters "I L O U".
ENCODING = "0123456789abcdefghjkmnpqrstvwxyz"
DECODING = dict((val, ind) for ind, val in enumerate(ENCODING))


def encode(value: hints.Buffer) -> str:
    """
    Encode the given :class:`~bytes` instance to a :class:`~str` using Base32 encoding.

    .. note:: You should only use this method if you've got a :class:`~bytes` instance
        and you are unsure of what it represents. If you know the the _meaning_ of the
        :class:`~bytes` instance, you should call the `encode_*` method explicitly for
        better performance.

    :param value: Bytes to encode
    :type value: :class:`~bytes`, :class:`~bytearray`, or :class:`~memoryview`
    :return: Value encoded as a Base32 string
    :rtype: :class:`~str`
    :raises ValueError: when the value is not 5 or 10 bytes long
    """
    length = len(value)

    # Order here is based on assumed hot path.
    if length == 10:
        return encode_serialid(value)
    if length == 5:
        return encode_segment(value)

    raise ValueError('Expects bytes in sizes of 5 or 10; got {}'.format(length))


def encode_segment(segment_bytes: hints.Buffer) -> str:
    """
    Encode the given buffer to a :class:`~str` using Base32 encoding.

    The given :class:`~bytes` are expected to represent the first 5 bytes of a SerialId, which
    are a segment in milliseconds.

    .. note:: This uses an optimized strategy from the `NUlid` project for encoding SerialId
        bytes specifically and is not meant for arbitrary encoding.

    :param segment: Bytes to encode
    :type segment: :class:`~bytes`, :class:`~bytearray`, or :class:`~memoryview`
    :return: Value encoded as a Base32 string
    :rtype: :class:`~str`
    :raises ValueError: when the segment is not 5 bytes
    """
    length = len(segment_bytes)
    if length != 5:
        raise ValueError('Expects 5 bytes for segment; got {}'.format(length))

    encoding = ENCODING
    # << >> SHIFT operators has higher precedence then AND / OR
    return \
        encoding[segment_bytes[0] >> 3 & 31] + \
        encoding[(segment_bytes[0] << 2 | segment_bytes[1] >> 6) & 31] + \
        encoding[segment_bytes[1] >> 1 & 31] + \
        encoding[(segment_bytes[1] << 4 | segment_bytes[2] >> 4) & 31] + \
        encoding[(segment_bytes[2] << 1 | segment_bytes[3] >> 7) & 31] + \
        encoding[segment_bytes[3] >> 2 & 31] + \
        encoding[(segment_bytes[3] << 3 | segment_bytes[4] >> 5) & 31] + \
        encoding[segment_bytes[4] & 31]


def encode_serialid(serial_bytes: hints.Buffer, separated: hints.Bool = True) -> str:
    """
    Encode the given buffer to a :class:`~str` using Base32 encoding.

    The given :class:`~bytes` are expected to represent the last 10 bytes of a SerialId, which
    are cryptographically secure random values.

    .. note:: This uses an optimized strategy from the `NUlid` project for encoding SerialId
        bytes specifically and is not meant for arbitrary encoding.

    :param serialid: Bytes to encode
    :type serialid: :class:`~bytes`, :class:`~bytearray`, or :class:`~memoryview`
    :return: Value encoded as a Base32 string
    :rtype: :class:`~str`
    :raises ValueError: when the serial id is not 10 bytes
    """
    length = len(serial_bytes)
    if length != 10:
        raise ValueError('Expects 10 bytes for serial (timestamp + randomness); got {}'.format(length))

    separator = '-' if separated else ''
    return encode_segment(serial_bytes[:5]) + separator + encode_segment(serial_bytes[5:])


def decode(value: str) -> bytes:
    """
    Decode the given Base32 encoded :class:`~str` instance to :class:`~bytes`.

    .. note:: You should only use this method if you've got a :class:`~str` instance
        and you are unsure of what it represents. If you know the the _meaning_ of the
        :class:`~str` instance, you should call the `decode_*` method explicitly for
        better performance.

    :param value: String to decode
    :type value: :class:`~str`
    :return: Value decoded from Base32 string
    :rtype: :class:`~bytes`
    :raises ValueError: when value is not 10, 16, or 26 characters
    :raises ValueError: when value cannot be encoded in ASCII
    """
    length = len(value)

    # Order here is based on assumed hot path.
    if length == 16 or length == 17:
        return decode_serialid(value)
    if length == 8:
        return decode_segment(value)

    raise ValueError('Expects string in lengths of 8 or 16/17 (<timestamp>-<randomness>) including hyphen; got {}'.format(length))


def decode_segment(segment: str) -> bytes:
    """
    Decode the given Base32 encoded :class:`~str` instance to :class:`~bytes`.

    The given :class:`~str` are expected to represent the 8 characters of a SerialId, which
    are the timestamp in centiseconds or randomness.

    :param timestamp: String to decode
    :type timestamp: :class:`~str`
    :return: Value decoded from Base32 string
    :rtype: :class:`~bytes`
    :raises ValueError: when value is not 8 characters
    :raises ValueError: when value cannot be encoded in ASCII
    """
    length = len(segment)
    if length != 8:
        raise ValueError('Expects 8 characters for decoding; got {}'.format(length))

    # try:
    #     b0 = DECODING[segment[0]]
    #     b1 = DECODING[segment[1]]
    #     b2 = DECODING[segment[2]]
    #     b3 = DECODING[segment[3]]
    #     b4 = DECODING[segment[4]]
    #     b5 = DECODING[segment[5]]
    #     b6 = DECODING[segment[6]]
    #     b7 = DECODING[segment[7]]
    # except KeyError as e:
    #     raise ValueError('Non-base32 character found: "{}"'.format(e.args[0]))

    b0 = encoded(segment[0])
    b1 = encoded(segment[1])
    b2 = encoded(segment[2])
    b3 = encoded(segment[3])
    b4 = encoded(segment[4])
    b5 = encoded(segment[5])
    b6 = encoded(segment[6])
    b7 = encoded(segment[7])

    return bytes((
        (b0 << 3 | b1 >> 2) & 255,
        (b1 << 6 | b2 << 1 | b3 >> 4) & 255,
        (b3 << 4 | b4 >> 1) & 255,
        (b4 << 7 | b5 << 2 | b6 >> 3) & 255,
        (b6 << 5 | b7) & 255
    ))


def decode_serialid(value: str) -> bytes:
    """
    Decode the given Base32 encoded :class:`~str` instance to :class:`~bytes`.

    The given :class:`~str` are expected to represent the 16 or 17 (<timestamp>-<randomness>) characters of a SerialId.

    :param value: String to decode
    :type value: :class:`~str`
    :return: Value decoded from Base32 string
    :rtype: :class:`~bytes`
    :raises ValueError: when value is not 17 characters
    :raises ValueError: when value cannot be encoded in ASCII
    """
    length = len(value)
    if length != 16 and length != 17:
        raise ValueError('Expects 16 or 17 (<timestamp>-<randomness>) characters for decoding may include hyphen; got {}'.format(length))

    return decode_segment(value[:8]) + decode_segment(value[-8:])


def encoded(en_symbol):
    if en_symbol == '0': return 0
    if en_symbol == '1': return 1
    if en_symbol == '2': return 2
    if en_symbol == '3': return 3
    if en_symbol == '4': return 4
    if en_symbol == '5': return 5
    if en_symbol == '6': return 6
    if en_symbol == '7': return 7
    if en_symbol == '8': return 8
    if en_symbol == '9': return 9
    if en_symbol == 'a': return 10
    if en_symbol == 'b': return 11
    if en_symbol == 'c': return 12
    if en_symbol == 'd': return 13
    if en_symbol == 'e': return 14
    if en_symbol == 'f': return 15
    if en_symbol == 'g': return 16
    if en_symbol == 'h': return 17
    if en_symbol == 'j': return 18
    if en_symbol == 'k': return 19
    if en_symbol == 'm': return 20
    if en_symbol == 'n': return 21
    if en_symbol == 'p': return 22
    if en_symbol == 'q': return 23
    if en_symbol == 'r': return 24
    if en_symbol == 's': return 25
    if en_symbol == 't': return 26
    if en_symbol == 'v': return 27
    if en_symbol == 'w': return 28
    if en_symbol == 'x': return 29
    if en_symbol == 'y': return 30
    if en_symbol == 'z': return 31

    raise ValueError('Non-base32 character found: "{}"'.format(en_symbol))

