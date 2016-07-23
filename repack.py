#!/usr/bin/env python3

import argparse
import io
import pathlib
import zlib

# The MIT License (MIT)
# Copyright (c) 2016 kyarei
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Usage: python3 repack.py <root dir> <archive name>

# Parse the arguments

parser = argparse.ArgumentParser(description='Repack Wizard101 WAD files.')
parser.add_argument('sourcePath', type=str,
    help='the root directory of the files to be archived')
parser.add_argument('archivePath', type=str,
    help='the path of the archive file to be made')
parser.add_argument('--verbose', '-v', type=bool,
    help='if enabled, use diagnostics')

args = parser.parse_args()

# Get all files in the directory specified

root = pathlib.Path(args.sourcePath)
files = root.glob("**/*");
entries = []
offset = 14 # Precalculate offset of data section in loop below

# Make entries of all files

for f in files:
    if f.is_file():
        with f.open(mode="rb") as h:
            contents = h.read(-1)
            compressedContents = zlib.compress(contents)
            uSize = len(contents)
            zSize = len(compressedContents)
            name = str(f.relative_to(root))
            isCompressed = zSize < uSize
            crc = zlib.crc32(contents)
            entry = {
                "contents": contents,
                "compressedContents": compressedContents,
                "uSize": uSize,
                "zSize": zSize,
                "name": name,
                "isCompressed": isCompressed,
                "crc": crc
            }
            entries.append(entry)
            offset += 22 + len(name)
            if args.verbose:
                print("> File %s acknowledged" % name)

if args.verbose:
    print("%d files acknowledged" % len(entries))

# Open the output file

out = open(args.archivePath, "wb");

def writeByte(stream, val):
    stream.write(bytes([val]))
def writeInt(stream, val):
    stream.write(val.to_bytes(4, byteorder="little"))

if args.verbose:
    print("Opened output file; writing data...")

# Write magic string
out.write(b"KIWAD")
# Write version
writeInt(out, 2)
# Write number of files
writeInt(out, len(entries))
# Write dummy byte
writeByte(out, 1)
# Write file ENTRIES
for e in entries:
    netSize = e["zSize"] if e["isCompressed"] else e["uSize"]
    writeInt(out, offset) # Offset
    writeInt(out, e["uSize"])
    writeInt(out, e["zSize"])
    writeByte(out, e["isCompressed"])
    writeInt(out, e["crc"])
    writeInt(out, len(e["name"].encode()) + 1) # includes terminating null
    out.write(e["name"].encode())
    writeByte(out, 0)
    offset += netSize
    if args.verbose:
        print("> Wrote ENTRY for %s" % e["name"])
# Write file DATA
for e in entries:
    out.write(e["compressedContents"] if e["isCompressed"] else e["contents"])
    if args.verbose:
        print("> Wrote DATA for %s" % e["name"])
