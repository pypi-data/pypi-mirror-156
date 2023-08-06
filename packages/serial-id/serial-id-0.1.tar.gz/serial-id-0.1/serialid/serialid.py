"""
    mysteryjeans/serial-id
    ~~~~~~~~~

    Serial Id of 10 bytes similar to SerialId.
"""
import binascii
import datetime
import typing

from . import hints, base32

__all__ = ['Timestamp', 'Randomness', 'SerialId']


#: Type hint that defines multiple primitive types and itself for comparing MemoryView instances.
MemoryViewPrimitive = typing.Union['MemoryView', hints.Primitive]  # pylint: disable=invalid-name


class MemoryView:
    """
    Wraps a buffer object, typically :class:`~bytes`, with a :class:`~memoryview` and provides easy
    type comparisons and conversions between presentation formats.
    """

    __slots__ = ['memory']

    def __init__(self, buffer: hints.Buffer) -> None:
        self.memory = memoryview(buffer)

    def __eq__(self, other: MemoryViewPrimitive) -> hints.Bool:  # type: ignore[override]
        if isinstance(other, MemoryView):
            return self.memory == other.memory
        if isinstance(other, (bytes, bytearray, memoryview)):
            return self.memory == other
        if isinstance(other, int):
            return self.int == other
        if isinstance(other, float):
            return self.float == other
        if isinstance(other, str):
            return self.str == other
        return NotImplemented

    def __ne__(self, other: MemoryViewPrimitive) -> hints.Bool:  # type: ignore[override]
        if isinstance(other, MemoryView):
            return self.memory != other.memory
        if isinstance(other, (bytes, bytearray, memoryview)):
            return self.memory != other
        if isinstance(other, int):
            return self.int != other
        if isinstance(other, float):
            return self.float != other
        if isinstance(other, str):
            return self.str != other
        return NotImplemented

    def __lt__(self, other: MemoryViewPrimitive) -> hints.Bool:
        if isinstance(other, MemoryView):
            return self.int < other.int
        if isinstance(other, (bytes, bytearray)):
            return self.bytes < other
        if isinstance(other, memoryview):
            return self.bytes < other.tobytes()
        if isinstance(other, int):
            return self.int < other
        if isinstance(other, float):
            return self.float < other
        if isinstance(other, str):
            return self.str < other
        return NotImplemented

    def __gt__(self, other: MemoryViewPrimitive) -> hints.Bool:
        if isinstance(other, MemoryView):
            return self.int > other.int
        if isinstance(other, (bytes, bytearray)):
            return self.bytes > other
        if isinstance(other, memoryview):
            return self.bytes > other.tobytes()
        if isinstance(other, int):
            return self.int > other
        if isinstance(other, float):
            return self.float > other
        if isinstance(other, str):
            return self.str > other
        return NotImplemented

    def __le__(self, other: MemoryViewPrimitive) -> hints.Bool:
        if isinstance(other, MemoryView):
            return self.int <= other.int
        if isinstance(other, (bytes, bytearray)):
            return self.bytes <= other
        if isinstance(other, memoryview):
            return self.bytes <= other.tobytes()
        if isinstance(other, int):
            return self.int <= other
        if isinstance(other, float):
            return self.float <= other
        if isinstance(other, str):
            return self.str <= other
        return NotImplemented

    def __ge__(self, other: MemoryViewPrimitive) -> hints.Bool:
        if isinstance(other, MemoryView):
            return self.int >= other.int
        if isinstance(other, (bytes, bytearray)):
            return self.bytes >= other
        if isinstance(other, memoryview):
            return self.bytes >= other.tobytes()
        if isinstance(other, int):
            return self.int >= other
        if isinstance(other, float):
            return self.float >= other
        if isinstance(other, str):
            return self.str >= other
        return NotImplemented

    def __hash__(self) -> hints.Int:
        return hash(self.memory)

    def __bytes__(self) -> hints.Bytes:
        return self.bytes

    def __float__(self) -> hints.Float:
        return self.float

    def __int__(self) -> hints.Int:
        return self.int

    def __index__(self) -> hints.Int:
        return self.int

    def __repr__(self) -> hints.Str:
        return '<{}({!r})>'.format(self.__class__.__name__, str(self))

    def __str__(self) -> hints.Str:
        return self.str

    def __getstate__(self) -> hints.Str:
        return self.str

    def __setstate__(self, state: hints.Str) -> None:
        self.memory = memoryview(base32.decode(state))

    @property
    def bin(self) -> hints.Str:
        """
        Computes the binary string value of the underlying :class:`~memoryview`.

        :return: Memory in binary string form
        :rtype: :class:`~str`
        """
        return bin(self.int)

    @property
    def bytes(self) -> hints.Bytes:
        """
        Computes the bytes value of the underlying :class:`~memoryview`.

        :return: Memory in bytes form
        :rtype: :class:`~bytes`
        """
        return self.memory.tobytes()

    @property
    def float(self) -> hints.Float:
        """
        Computes the float value of the underlying :class:`~memoryview` in big-endian byte order.

        :return: Bytes in float form.
        :rtype: :class:`~float`
        """
        return float(self.int)

    @property
    def hex(self) -> hints.Str:
        """
        Computes the hexadecimal string value of the underlying :class:`~memoryview`.

        :return: Memory in hexadecimal string form
        :rtype: :class:`~str`
        """
        return '0x' + binascii.hexlify(self.bytes).decode()

    @property
    def int(self) -> hints.Int:
        """
        Computes the integer value of the underlying :class:`~memoryview` in big-endian byte order.

        :return: Bytes in integer form.
        :rtype: :class:`~int`
        """
        return int.from_bytes(self.memory, byteorder='big')

    @property
    def oct(self) -> hints.Str:
        """
        Computes the octal string value of the underlying :class:`~memoryview`.

        :return: Memory in octal string form
        :rtype: :class:`~str`
        """
        return oct(self.int)

    @property
    def str(self) -> hints.Str:
        """
        Computes the string value of the underlying :class:`~memoryview` in Base32 encoding.

        .. note:: The base implementation here will call :func:`~ulid.base32.encode` which
        performs analysis on the bytes to determine how it should be decoded. This is going to
        be slightly slower than calling the explicit `encode_*` methods so each model that
        derives from this class can/should override and specify the explicit function to call.

        :return: Bytes in Base32 string form.
        :rtype: :class:`~str`
        :raises ValueError: if underlying :class:`~memoryview` cannot be encoded
        """
        return base32.encode(self.memory)


class Timestamp(MemoryView):
    """
    Represents the timestamp portion of a SerialId.

    * Unix time (time since epoch) in centiseconds.
    * First 40 bits of SerialId when in binary format.
    * First 8 characters of SerialId when in string format.
    """

    __slots__ = MemoryView.__slots__

    @property
    def str(self) -> hints.Str:
        """
        Computes the string value of the timestamp from the underlying :class:`~memoryview` in Base32 encoding.

        :return: Timestamp in Base32 string form.
        :rtype: :class:`~str`
        :raises ValueError: if underlying :class:`~memoryview` cannot be encoded
        """
        return base32.encode_segment(self.memory)

    @property
    def timestamp(self) -> hints.Float:
        """
        Computes the Unix time (seconds since epoch) from its :class:`~memoryview`.

        :return: Timestamp in Unix time (seconds since epoch) form.
        :rtype: :class:`~float`
        """
        return self.int / 100.0

    @property
    def datetime(self) -> hints.Datetime:
        """
        Creates a :class:`~datetime.datetime` instance (assumes UTC) from the Unix time value of the timestamp
        with centiseconds precision.

        :return: Timestamp in datetime form.
        :rtype: :class:`~datetime.datetime`
        """
        centi = self.int
        sec = centi // 100.0
        micro = (centi % 100) * 10 * 1000

        return datetime.datetime.fromtimestamp(sec).replace(microsecond=micro)


class Randomness(MemoryView):
    """
    Represents the randomness portion of a SerialId.

    * Cryptographically secure random values.
    * Last 40 bits of SerialId when in binary format.
    * Last 8 characters of SerialId when in string format.
    """

    __slots__ = MemoryView.__slots__

    @property
    def str(self) -> hints.Str:
        """
        Computes the string value of the randomness from the underlying :class:`~memoryview` in Base32 encoding.

        :return: Timestamp in Base32 string form.
        :rtype: :class:`~str`
        :raises ValueError: if underlying :class:`~memoryview` cannot be encoded
        """
        return base32.encode_segment(self.memory)


class SerialId(MemoryView):
    """
    Represents a Serial Id.

    * 80 bits in binary format.
    * 17 characters in string format separated by "-".
    * 10 octets.
    * Network byte order, big-endian, most significant bit first.
    """

    __slots__ = MemoryView.__slots__

    @property
    def str(self) -> hints.Str:
        """
        Computes the string value of the SerialId from its :class:`~memoryview` in Base32 encoding.

        :return: SerialId in Base32 string form in <timestamp>-<randomness>.
        :rtype: :class:`~str`
        :raises ValueError: if underlying :class:`~memoryview` cannot be encoded
        """
        return base32.encode_serialid(self.memory, True)

    @property
    def str16(self) -> hints.Str:
        """
        Computes the string value of the SerialId from its :class:`~memoryview` in Base32 encoding.

        :return: SerialId in Base32 string form.
        :rtype: :class:`~str`
        :raises ValueError: if underlying :class:`~memoryview` cannot be encoded
        """
        return base32.encode_serialid(self.memory, False)

    def timestamp(self) -> Timestamp:
        """
        Creates a :class:`~serialid.serialid.Timestamp` instance that maps to the first 40 bits of this SerialId.

        :return: Timestamp from first 40 bits.
        :rtype: :class:`~serialid.serialid.Timestamp`
        """
        return Timestamp(self.memory[:5])

    def randomness(self) -> Randomness:
        """
        Creates a :class:`~serialid.serialid.Randomness` instance that maps to the last 40 bits of this SerialId.

        :return: Timestamp from first 40 bits.
        :rtype: :class:`~serialid.serialid.Timestamp`
        """
        return Randomness(self.memory[5:])