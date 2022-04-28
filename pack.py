#!/usr/bin/python3
import subprocess
import tempfile
import sys

"""
Copyright © 2022 Hexalinq.
Web: https://hexalinq.com/
Email: info@hexalinq.com

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

try:
	infile = sys.argv[1]
	outfile = sys.argv[2]
except:
	print(f"Usage: {sys.argv[0]} <infile.sh> <outfile.elf>")
	exit(1)

def encode_bytes(data):
	encoded = []
	for byte in data: encoded.append(hex(byte))
	return ", ".join(encoded)

print(f"[*] Reading shell script from {infile}")
with open(infile, "rb") as file: data = file.read()

print(f"[*] Reading C template from ./template.c")
with open("template.c", "rb") as file: template = file.read()

print(f"[*] Generating XOR key")
with open("/dev/urandom", "rb") as file: key = file.read(128)

print(f"[*] Encrypting input")
data = bytearray(data)
for index in range(len(data)): data[index] ^= key[index % len(key)]

key = encode_bytes(key)
script = encode_bytes(bytes(data))
source = template.replace(b"@SCRIPT", script.encode("ascii")).replace(b"@KEY", key.encode("ascii"))

print(f"[*] Compiling generated source file")
with tempfile.NamedTemporaryFile() as file:
	file.file.write(source)
	file.file.flush()
	status = subprocess.call(["gcc", "-s", "-Os", "-static", "-fPIC", "-fwhole-program", "-o", outfile, "-xc", file.name])
	if status: exit(status)

print(f"[*] Compressing output with UPX")
try: status = subprocess.call(["upx", "-q", "--best", "--ultra-brute", outfile], stdout = subprocess.DEVNULL)
except FileNotFoundError: print("[-] UPX is not installed; skipping compression stage")

print(f"[+] Output saved as {outfile}")
exit(status)
