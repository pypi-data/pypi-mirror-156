"""
    serialid/api/api
    ~~~~~~~~~~~~

    Contains functionality for public API methods for the 'serialid' package.
"""
import typing
from . import codec, hints, providers, base32, serialid

#: Type hint that defines multiple primitive types that can represent a full SerialId.
SerialIdPrimitive = typing.Union[hints.Primitive, serialid.SerialId]  # pylint: disable=invalid-name

#: Defines the '__all__' for the API interface.
__all__ = [
    'new',
    'new_seq',
    'parse',
    'create',
    'from_bytes',
    'from_int',
    'from_str',
    'from_timestamp',
    'from_randomness',
]

class Api:
    """
    Encapsulates public API methods for the 'serialid' package that is agnostic to the underlying provider.
    """
    def __init__(self, provider: providers.Provider) -> None:
        """
        Create a new API instance with the given provider.

        :param provider: Provider that yields timestamp/randomness values.
        :type provider: :class:`~serialid.providers.Provider`
        """
        self.provider = provider

    def new(self) -> serialid.SerialId:
        """
        Create a new :class:`~serialid.serialid.SerialId` instance.

        The timestamp and randomness values are created from
        the instance :class:`~serialid.providers.Provider`.

        :return: SerialId from current timestamp
        :rtype: :class:`~serialid.serialid.SerialId`
        """
        timestamp, randomness = self.provider.new()
        return serialid.SerialId(timestamp + randomness)

    def new_seq(self, from_serial_id: serialid.SerialId) -> serialid.SerialId:
        """
        Create a new sequential :class:`~serialid.serialid.SerialId` instance.

        :param value: SerialId value of any supported type
        :type value: :class:`~serialid.serialid.SerialId`
        :return: SerialId new sequential id from current timestamp
        :rtype: :class:`~serialid.serialid.SerialId`
        """
        seq_id = self.new()
        if from_serial_id.timestamp() == seq_id.timestamp() and from_serial_id.randomness() >= seq_id.randomness():
            seq_id = self.from_int(from_serial_id.int + 1)

        return seq_id

    def parse(self, value: SerialIdPrimitive) -> serialid.SerialId:
        """
        Create a new :class:`~serialid.serialid.SerialId` instance from the given value.

        .. note:: This method should only be used when the caller is trying to parse a SerialId from
        a value when they're unsure what format/primitive type it will be given in.

        :param value: SerialId value of any supported type
        :type value: :class:`~serialid.api.SerialIdPrimitive`
        :return: SerialId from value
        :rtype: :class:`~serialid.serialid.SerialId`
        :raises ValueError: when unable to parse a SerialId from the value
        """
        if isinstance(value, serialid.SerialId):
            return value
        if isinstance(value, str):
            return self.from_str(value)
        if isinstance(value, (int, float)):
            return self.from_int(int(value))
        if isinstance(value, (bytes, bytearray)):
            return self.from_bytes(value)
        if isinstance(value, memoryview):
            return self.from_bytes(value.tobytes())
        raise ValueError('Cannot create SerialId from type {}'.format(value.__class__.__name__))

    def from_timestamp(self, timestamp: codec.TimestampPrimitive) -> serialid.SerialId:
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

        :param timestamp: Timestamp in milliseconds
        :type timestamp: See docstring for types
        :return: SerialId using given timestamp and new randomness
        :rtype: :class:`~serialid.serialid.SerialId`
        :raises ValueError: when the value is an unsupported type
        :raises ValueError: when the value is a string and cannot be Base32 decoded
        :raises ValueError: when the value is or was converted to something 40 bits
        """
        timestamp = codec.decode_timestamp(timestamp)
        randomness = self.provider.randomness(timestamp.bytes)
        return self.create(timestamp, randomness)

    def from_randomness(self, randomness: codec.RandomnessPrimitive) -> serialid.SerialId:
        """
        Create a new :class:`~serialid.serialid.SerialId` instance using the given randomness value of a supported type.

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
        timestamp = self.provider.timestamp()
        return self.create(timestamp, randomness)

    @staticmethod
    def create(timestamp: codec.TimestampPrimitive, randomness: codec.RandomnessPrimitive) -> serialid.SerialId:
        """
        Create a new :class:`~serialid.serialid.SerialId` instance using the given timestamp and randomness values.

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

        The following types are supported for randomness values:

        * :class:`~int`
        * :class:`~float`
        * :class:`~str`
        * :class:`~memoryview`
        * :class:`~serialid.serialid.Randomness`
        * :class:`~serialid.serialid.SerialId`
        * :class:`~bytes`
        * :class:`~bytearray`

        :param timestamp: Unix timestamp in seconds
        :type timestamp: See docstring for types
        :param randomness: Random bytes
        :type randomness: See docstring for types
        :return: SerialId using given timestamp and randomness
        :rtype: :class:`~serialid.serialid.SerialId`
        :raises ValueError: when a value is an unsupported type
        :raises ValueError: when a value is a string and cannot be Base32 decoded
        :raises ValueError: when a value is or was converted to incorrect bit length
        """
        timestamp = codec.decode_timestamp(timestamp)
        randomness = codec.decode_randomness(randomness)
        return serialid.SerialId(timestamp.bytes + randomness.bytes)

    @staticmethod
    def from_bytes(value: hints.Buffer) -> serialid.SerialId:
        """
        Create a new :class:`~serialid.serialid.SerialId` instance from the given :class:`~bytes`,
        :class:`~bytearray`, or :class:`~memoryview` value.

        :param value: 16 bytes
        :type value: :class:`~bytes`, :class:`~bytearray`, or :class:`~memoryview`
        :return: SerialId from buffer value
        :rtype: :class:`~serialid.serialid.SerialId`
        :raises ValueError: when the value is not 16 bytes
        """
        length = len(value)
        if length != 10:
            raise ValueError('Expects bytes to be 80 bits; got {} bytes'.format(length))

        return serialid.SerialId(value)

    @staticmethod
    def from_int(value: int) -> serialid.SerialId:
        """
        Create a new :class:`~serialid.serialid.SerialId` instance from the given :class:`~int` value.

        :param value: 80 bit integer
        :type value: :class:`~int`
        :return: SerialId from integer value
        :rtype: :class:`~serialid.serialid.SerialId`
        :raises ValueError: when the value is less then 80 bit integer
        """
        if value < 0:
            raise ValueError('Expects positive integer')

        length = (value.bit_length() + 7) // 8
        if length < 10:
            raise ValueError('Expects integer to be more then 80 bits; got {} bytes'.format(length))

        return serialid.SerialId(value.to_bytes(10, byteorder='big'))

    @staticmethod
    def from_str(value: str) -> serialid.SerialId:
        """
        Create a new :class:`~serialid.serialid.SerialId` instance from the given :class:`~str` value.

        :param value: Base32 encoded string
        :type value: :class:`~str`
        :return: SerialId from string value
        :rtype: :class:`~serialid.serialid.SerialId`
        :raises ValueError: when the value is not 16 characters or malformed
        """
        len_value = len(value)
        if len_value == 16 or len_value == 17:
            return serialid.SerialId(base32.decode(value))

        raise ValueError('Cannot create SerialId from string of length {}'.format(len_value))


DEFAULT = Api(providers.DEFAULT)

create = DEFAULT.create
from_bytes = DEFAULT.from_bytes
from_int = DEFAULT.from_int
from_randomness = DEFAULT.from_randomness
from_str = DEFAULT.from_str
from_timestamp = DEFAULT.from_timestamp
new = DEFAULT.new
new_seq = DEFAULT.new_seq
parse = DEFAULT.parse
