"""
    serialid/consts
    ~~~~~~~~~~~

    Contains public API constant values.
"""
from . import serialid
from . import providers

__all__ = ['MIN_TIMESTAMP', 'MAX_TIMESTAMP', 'MIN_RANDOMNESS', 'MAX_RANDOMNESS', 'MIN_SERIALID', 'MAX_SERIALID']


#: Minimum possible timestamp value (0).
MIN_TIMESTAMP = serialid.Timestamp(b'\x00\x00\x00\x00\x00')


#: Maximum possible timestamp value (<needs to be calculated> epoch).
MAX_TIMESTAMP = serialid.Timestamp(b'\xff\xff\xff\xff\xff')


#: Minimum possible randomness value (0).
MIN_RANDOMNESS = serialid.Randomness(b'\x00\x00\x00\x00\x00')


#: Maximum possible randomness value (1099511627775).
MAX_RANDOMNESS = serialid.Randomness(b'\xff\xff\xff\xff\xff')


#: Minimum possible SerialId value (0).
MIN_SERIALID = serialid.SerialId(MIN_TIMESTAMP.bytes + MIN_RANDOMNESS.bytes)


#: Maximum possible SerialId value (1208925819614629174706175).
MAX_SERIALID = serialid.SerialId(MAX_TIMESTAMP.bytes + MAX_RANDOMNESS.bytes)
