#!/usr/bin/env python3
from pwn import remote
import base64
from collections import defaultdict

HOST = "5fae087d014badc8.chal.ctf.ae"
PORT = 443

BLOCK_BITS = 96
HALF = BLOCK_BITS // 2
MASK = (1 << HALF) - 1

def b64e(x: bytes) -> str:
    return base64.urlsafe_b64encode(x).decode().strip("=")

def b64d(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "===")

def pad_to_block(msg: bytes) -> int:
    pbyt = b'\x01' + msg
    pint = int.from_bytes(pbyt, 'big')
    pint = (pint << 1) | 1
    plen = pint.bit_length() % BLOCK_BITS
    if plen:
        pint <<= (BLOCK_BITS - plen)
    return pint

def L0_from_msg(msg: bytes):
    pint = pad_to_block(msg)
    return pint >> HALF, pint & MASK

def recv_until_cipher(io):
    while True:
        line = io.recvline().decode(errors="ignore").strip()
        if '[~]' in line:
            return line

io = remote(HOST, PORT, ssl=True, sni=HOST)
io.recvuntil(b'> ')

pairs = []

count = 0
for b1 in range(256):
    for b2 in range(256):
        msg = bytes([b1, b2])

        io.sendline(b'E')
        io.recvuntil(b'(B64) ')
        io.sendline(b64e(msg).encode())

        line = recv_until_cipher(io)
        ct_b64 = line.split()[-1]
        ct = b64d(ct_b64)
        ct_int = int.from_bytes(ct, 'big')

        L11 = ct_int >> HALF
        R11 = ct_int & MASK
        L0, R0 = L0_from_msg(msg)

        pairs.append((msg, L0, R0, L11, R11))

        count += 1
        if count % 5000 == 0:
            print(f"[+] {count}/65536 collected")

io.close()

print("[+] Total pairs:", len(pairs))

groups = defaultdict(list)
for p in pairs:
    groups[p[3]].append(p)

collisions = [g for g in groups.values() if len(g) > 1]
print("[+] Collision groups:", len(collisions))
