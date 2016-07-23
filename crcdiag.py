import sys
import zlib

h = open(sys.argv[1], mode="rb")
contents = h.read(-1)
compressedContents = zlib.compress(contents)
goal = int(sys.argv[2])

for i in range(0, 0x100000000):
    if zlib.crc32(contents, i) == goal:
        print("CRC32: %d matches" % i)
    if zlib.adler32(contents, i) == goal:
        print("Adler32: %d matches" % i)
    if i & 0xFFFFF == 0:
        print("Progress: %d" % i)
