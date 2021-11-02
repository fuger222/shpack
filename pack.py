#!/usr/bin/python3
import subprocess
import tempfile
import sys

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

print(f"[*] Reading shell script from {outfile}")
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
