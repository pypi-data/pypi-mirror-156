# Serial-Id

[![codecov](https://codecov.io/gh/mysteryjeans/serial-id/branch/master/graph/badge.svg)](https://codecov.io/gh/mysteryjeans/serial-id)
[![Code Climate](https://codeclimate.com/github/mysteryjeans/serial-id/badges/gpa.svg)](https://codeclimate.com/github/mysteryjeans/serial-id)
[![Issue Count](https://codeclimate.com/github/mysteryjeans/serial-id/badges/issue_count.svg)](https://codeclimate.com/github/mysteryjeans/serial-id)

## Sequential Unique Short & Sortable Identifier

It is a short sequential identifier that is random but sortable and only uses 80 bits. First 40 bits are for timestamp and rest of the 40 bits are used for randomness.

### Why's Serial-Id?

This is a conversion of [ahawker/ulid](https://github.com/ahawker/ulid) 128 bits implementation to short 80 bits identifier with purpose of sortability and uses Crockford's [Base32](https://www.crockford.com/base32.html) encoding

### Installation

To install serial-id from [github](https://github.com/mysteryjeans/serial-id.git):
```bash
    $ pip install --upgrade git+https://github.com/mysteryjeans/serial-id.git
```

To install serial-id from source:
```bash
    $ git clone https://github.com/mysteryjeans/serial-id.git
    $ cd serial-id && python setup.py install
```

### Usage

Create a brand new SerialId.

The timestamp value (40-bits) is from [time.time()](https://docs.python.org/3/library/time.html?highlight=time.time#time.time) with centiseconds precision.

The randomness value (40-bits) is from [os.urandom()](https://docs.python.org/3/library/os.html?highlight=os.urandom#os.urandom).

```python
import serialid
serialid.new()
<SerialId('4t8ax5bs-6gvqk2sy')>
```

### Sequential Ids but with randomness

Create a new SerialId from an existing 80-bit value with guaranteed sort order.

```python
import serialid
seq_ids = []
new_sid = serialid.new()

for _ in range(0, 1000):
    new_sid = serialid.new_seq(new_sid)
    seq_ids.append(new_sid)

seq_ids[:10]
```

Create a new SerialId from an existing timestamp value, such as a [datetime](https://docs.python.org/3/library/datetime.html#module-datetime) object.

Supports timestamp values as `int`, `float`, `str`, `bytes`, `bytearray`, `memoryview`, `datetime`, `Timestamp`, and `SerialId` types.

```python
import datetime, serialid
serialid.from_timestamp(datetime.datetime(1999, 1, 1))
<SerialId('4t8ax5bs-6gvqk2sy')>
```

Create a new SerialId from an existing randomness value.

Supports randomness values as `int`, `float`, `str`, `bytes`, `bytearray`, `memoryview`, `Randomness` types.

```python
import os, serialid
randomness = os.urandom(10)
serialid.from_randomness(randomness)
<SerialId('4t8ax5bs-sgx82mz4')>
```

For cases when you don't necessarily control the data type (input from external system), you can use the `parse` method
which will attempt to make the correct determination for you. Please note that this will be slightly slower than creating
the instance from the respective `from_*` method as it needs to make a number of type/conditional checks.

Supports values as `int`, `float`, `str`, `bytes`, `bytearray`, `memoryview`, and `SerialId` types.

```python
import serialid
value = db.model.get_id()  ## Unsure about datatype -- Could be int or string?
serialid.parse(value) # Parses from str, int, float, bytes ...
<SerialId('4t8ax5bs-vp61yjkk')>
```

Once you have a SerailId object, there are a number of ways to interact with it.

The `timestamp` method will give you a snapshot view of the first 40-bits of the SerialId while the `randomness` method
will give you a snapshot of the last 40-bits.

```python
import serialid
id = serialid.new()
id
<SerialId('4t8ax5bs-vp61yjkk')>
id.timestamp()
<Timestamp('4t8ax5bs')>
id.randomness()
<Randomness('vp61yjkk')>
```

The `SerialId`, `Timestamp`, and `Randomness` classes all derive from the same base class, a `MemoryView`.

A `MemoryView` provides the `bin`, `bytes`, `hex`, `int`, `oct`, and `str`, methods for changing any values representation.

```python
import serialid
u = serialid.new()
u
<SerialId('4t8ax5bs-vp61yjkk')
u.timestamp()
<Timestamp('4t8ax5bs')>
u.timestamp().int
165636436000
u.timestamp().bytes
b'&\x90\xb3j\x13'
u.timestamp().datetime
datetime.datetime(2022, 6, 28, 2, 12, 1, 190000)
u.randomness().bytes
b'\x01c.)\xfa'
u.bytes[5:] == u.randomness().bytes
True
u.str
'4t8ax5bs-vp61yjkk'
u.int
182119165340642244955695
u.bin
'0b100110100100001011001100100001111000001001111100111101001011100000111000101111'
u.hex
'0x2690b321e09f3d2e0e2f'
u.oct
'0o46441314417011747513407057'
```

A `MemoryView` also provides rich comparison functionality.

```python
import datetime, time, serialid
u1 = serialid.new()
time.sleep(5)
u2 = serialid.new()
u1 < u2
True
u3 = serialid.from_timestamp(datetime.datetime(2039, 1, 1))
u1 < u2 < u3
True
[u.timestamp().datetime for u in sorted([u2, u3, u1])]
[datetime.datetime(2022, 6, 28, 2, 24, 56, 700000),
 datetime.datetime(2022, 6, 28, 2, 25, 1, 710000),
 datetime.datetime(2039, 1, 1, 0, 0)]
```

### Contributing

If you would like to contribute, simply fork the repository, push your changes and send a pull request.
Pull requests will be brought into the `master` branch via a rebase and fast-forward merge with the goal of having a linear branch history with no merge commits.

### License

[MIT License](LICENSE)

## Why not ULID?

SerailId provides:

* 80-bit sortable Ids
* 1099511627776 unique Serial Ids per centisecond 100th of a second
* Lexicographically sortable!
* Canonically encoded as a 16 character string, as opposed to the 24 character ULID
* Uses Crockford's base32 for better efficiency and readability (5 bits per character)
* Case insensitive
* No special characters (URL safe)

## Specification

Below is the current specification of ULID as implemented in this repository.

The binary format is implemented.

```
  4t8ax5bs           vp61yjkk

|----------|       |----------|
 Timestamp          Randomness
   8chars             8chars
   40bits             40bits
```

### Components

**Timestamp**
* 40 bit integer
* UNIX-time in centiseconds
* Won't run out of space till the year 2322 (300 years).

**Randomness**
* 40 bits
* Cryptographically secure source of randomness, if possible

### Sorting

The left-most character must be sorted first, and the right-most character sorted last (lexical order).
The default ASCII character set must be used. Within the same centiseconds, use `serialid.new_seq` to guaranteed sort order

### Encoding

Crockford's Base32 is used as shown. This alphabet excludes the letters I, L, O, and U to avoid confusion and abuse.

```
0123456789abcdefghjkmnpqrstvwxyz
```

### String Representation

```
ttttttttrrrrrrrr

where
t is Timestamp
r is Randomness
```

### Links

* [ULID Implementation (Python)](https://github.com/ahawker/ulid)
