#!/usr/bin/env python3
# This file is part of Xpra.
# Copyright (C) 2011-2021 Antoine Martin <antoine@xpra.org>
# Copyright (C) 2008, 2009, 2010 Nathaniel Smith <njs@pobox.com>
# Xpra is released under the terms of the GNU GPL v2, or, at your option, any
# later version. See the file COPYING for details.

from collections import namedtuple

from xpra.util import envbool, envint
from xpra.net.header import LZ4_FLAG, ZLIB_FLAG, BROTLI_FLAG


#MIN_COMPRESS_SIZE = envint("XPRA_MAX_DECOMPRESSED_SIZE", 512)
MIN_COMPRESS_SIZE = envint("XPRA_MAX_DECOMPRESSED_SIZE", -1)
MAX_DECOMPRESSED_SIZE = envint("XPRA_MAX_DECOMPRESSED_SIZE", 256*1024*1024)

#all the compressors we know about, in best compatibility order:
ALL_COMPRESSORS = ("zlib", "lz4", "brotli", "none")
#order for performance:
PERFORMANCE_ORDER = ("none", "lz4", "zlib", "brotli")
#require compression (disallow 'none'):
PERFORMANCE_COMPRESSION = ("lz4", "zlib", "brotli")

Compression = namedtuple("Compression", ["name", "version", "python_version", "compress", "decompress"])

COMPRESSION = {}


def init_lz4():
    from lz4 import VERSION, block
    import struct
    block_compress = block.compress
    block_decompress = block.decompress
    LZ4_HEADER = struct.Struct(b'<L')
    try:
        from lz4 import library_version_string
        version = library_version_string()
    except ImportError:
        from lz4.version import version
    def lz4_compress(packet, level):
        flag = min(15, level) | LZ4_FLAG
        if level>=9:
            return flag, block_compress(packet, mode="high_compression", compression=level)
        if level<=3:
            return flag, block_compress(packet, mode="fast", acceleration=8-level*2)
        return flag, block_compress(packet)
    def lz4_decompress(data):
        size = LZ4_HEADER.unpack_from(data[:4])[0]
        #it would be better to use the max_size we have in protocol,
        #but this hardcoded value will do for now
        if size>MAX_DECOMPRESSED_SIZE:
            sizemb = size//1024//1024
            maxmb = MAX_DECOMPRESSED_SIZE//1024//1024
            raise Exception("uncompressed data is too large: %iMB, limit is %iMB" % (sizemb, maxmb))
        return block_decompress(data)
    return Compression("lz4", version, VERSION.encode("latin1"), lz4_compress, lz4_decompress)

def init_brotli():
    import brotli
    def brotli_compress(packet, level):
        if len(packet)>1024*1024:
            level = min(9, level)
        else:
            level = min(11, level)
        if not isinstance(packet, (bytes, bytearray, memoryview)):
            packet = bytes(str(packet), 'UTF-8')
        return level | BROTLI_FLAG, brotli.compress(packet, quality=level)
    return Compression("brotli", None, brotli.__version__, brotli_compress, brotli.decompress)

def init_zlib():
    import zlib
    def zlib_compress(packet, level):
        level = min(9, max(1, level))
        if not isinstance(packet, (bytes, bytearray, memoryview)):
            packet = bytes(str(packet), 'UTF-8')
        return level + ZLIB_FLAG, zlib.compress(packet, level)
    def zlib_decompress(data):
        d = zlib.decompressobj()
        v = d.decompress(data, MAX_DECOMPRESSED_SIZE)
        assert not d.unconsumed_tail, "not all data was decompressed"
        return v
    return Compression("zlib", None, zlib.__version__, zlib_compress, zlib_decompress)

def init_none():
    def nocompress(packet, _level):
        if not isinstance(packet, bytes):
            packet = bytes(str(packet), 'UTF-8')
        return 0, packet
    def nodecompress(v):
        return v
    return Compression("none", None, None, nocompress, nodecompress)


def init_compressors(*names):
    for x in names:
        if not envbool("XPRA_%s" % (x.upper()), True):
            continue
        fn = globals().get("init_%s" % x)
        try:
            c = fn()
            assert c
            COMPRESSION[x] = c
        except (TypeError, ImportError, AttributeError):
            from xpra.log import Logger
            logger = Logger("network", "protocol")
            logger.debug("no %s", x, exc_info=True)

def init_all():
    init_compressors(*(list(ALL_COMPRESSORS)+["none"]))


def use(compressor) -> bool:
    return compressor in COMPRESSION


def get_compression_caps() -> dict:
    caps = {}
    for x in ALL_COMPRESSORS:
        c = COMPRESSION.get(x)
        if c is None:
            continue
        ccaps = caps.setdefault(x, {})
        if c.version:
            ccaps["version"] = c.version
        if c.python_version:
            pcaps = ccaps.setdefault("python-%s" % x, {})
            pcaps[""] = True
            if c.python_version is not None:
                pcaps["version"] = c.python_version
        ccaps[""] = True
    return caps

def get_enabled_compressors(order=ALL_COMPRESSORS):
    return tuple(x for x in order if x in COMPRESSION)

def get_compressor(name):
    c = COMPRESSION.get(name)
    assert c is not None, "'%s' compression is not supported" % name
    return c.compress


class Compressed:
    __slots__ = ("datatype", "data", "can_inline")
    def __init__(self, datatype, data, can_inline=False):
        assert data is not None, "compressed data cannot be set to None"
        self.datatype = datatype
        self.data = data
        self.can_inline = can_inline
    def __len__(self):
        return len(self.data)
    def __repr__(self):
        return  "Compressed(%s: %i bytes)" % (self.datatype, len(self.data))


class LevelCompressed(Compressed):
    __slots__ = ("level", "algorithm")
    def __init__(self, datatype, data, level, algo, can_inline):
        super().__init__(datatype, data, can_inline)
        self.level = level
        self.algorithm = algo
    def __repr__(self):
        return  "LevelCompressed(%s: %i bytes as %s/%i)" % (self.datatype, len(self.data), self.algorithm, self.level)


class LargeStructure:
    __slots__ = ("datatype", "data")
    def __init__(self, datatype, data):
        self.datatype = datatype
        self.data = data
    def __len__(self):
        return len(self.data)
    def __repr__(self):
        return  "LargeStructure(%s: %i bytes)" % (self.datatype, len(self.data))

class Compressible(LargeStructure):
    __slots__ = ()
    #wrapper for data that should be compressed at some point,
    #to use this class, you must override compress()
    def __repr__(self):
        return  "Compressible(%s: %i bytes)" % (self.datatype, len(self.data))
    def compress(self):
        raise Exception("compress() not defined on %s" % self)


def compressed_wrapper(datatype, data, level=5, can_inline=True, **kwargs):
    size = len(data)
    def no():
        return Compressed("raw %s" % datatype, data, can_inline=can_inline)
    if size<=MIN_COMPRESS_SIZE:
        #don't bother
        return no()
    if size>MAX_DECOMPRESSED_SIZE:
        sizemb = size//1024//1024
        maxmb = MAX_DECOMPRESSED_SIZE//1024//1024
        raise Exception("uncompressed data is too large: %iMB, limit is %iMB" % (sizemb, maxmb))
    try:
        algo = next(x for x in PERFORMANCE_COMPRESSION if kwargs.get(x) and x in COMPRESSION)
    except StopIteration:
        return no()
        #raise InvalidCompressionException("no compressors available")
    #TODO: smarter selection of algo based on datatype
    #ie: 'text' -> brotli
    c = COMPRESSION[algo]
    cl, cdata = c.compress(data, level)
    min_saving = kwargs.get("min_saving", 0)
    if len(cdata)>=size+min_saving:
        return no()
    return LevelCompressed(datatype, cdata, cl, algo, can_inline=can_inline)


class InvalidCompressionException(Exception):
    pass


def get_compression_type(level) -> str:
    if level & LZ4_FLAG:
        return "lz4"
    if level & BROTLI_FLAG:
        return "brotli"
    return "zlib"


def decompress(data, level):
    #log.info("decompress(%s bytes, %s) type=%s", len(data), get_compression_type(level))
    if level & LZ4_FLAG:
        algo = "lz4"
    elif level & BROTLI_FLAG:
        algo = "brotli"
    else:
        algo = "zlib"
    return decompress_by_name(data, algo)

def decompress_by_name(data, algo):
    c = COMPRESSION.get(algo)
    if c is None:
        raise InvalidCompressionException("%s is not available" % algo)
    return c.decompress(data)


def main(): # pragma: no cover
    from xpra.util import print_nested_dict
    from xpra.platform import program_context
    with program_context("Compression", "Compression Info"):
        init_all()
        print_nested_dict(get_compression_caps())


if __name__ == "__main__":  # pragma: no cover
    main()
