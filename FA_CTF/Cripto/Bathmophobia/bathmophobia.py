#!/usr/bin/env python3
#
# Dubai Police CTF 2025 Finals :: Bathmophobia
#
# By Polymero
#

#------------------------------------------------------------------------------------------------------------------------------#
#   IMPORTS                                                                                                                    #
#------------------------------------------------------------------------------------------------------------------------------#
# Documentation imports
from __future__ import annotations
from typing import Tuple, List, Dict, NewType, Union

# Native imports
import os   
import base64
from secrets import randbelow

# External dependencies
from Crypto.Cipher import AES   # pip install pycryptodome
from Crypto.Util.Padding import pad

# Flag import
FLAG = os.environ.get('DYN_FLAG', 'flag{D3BUGG1NG_1S_FUN}')
if isinstance(FLAG, str):
    FLAG = FLAG.encode()

#------------------------------------------------------------------------------------------------------------------------------#
#   UTILITY FUNCTIONS                                                                                                          #
#------------------------------------------------------------------------------------------------------------------------------#
def B64Encode(x: bytes) -> str:
    """ Encodes a bytestring into url-safe base64. """
    return base64.urlsafe_b64encode(x).decode().strip('=')

def B64Decode(x: str) -> bytes:
    """ Decodes a url-safe base64 string into bytes. """
    return base64.urlsafe_b64decode(x.encode() + b'===')

#------------------------------------------------------------------------------------------------------------------------------#
#   CHALLENGE CLASSES                                                                                                          #
#------------------------------------------------------------------------------------------------------------------------------#
class LCG:
    """ Linear Congruential Generator """
    def __init__(self, a: int, c: int, x0: int, mbit: int) -> None:
        self.a = a
        self.c = c
        self.m = 2 ** mbit - 1
        self.x = x0
        
    # Public methods
        
    def Get(self) -> int:
        """ Updates and outputs inner state. """
        self.x = (self.a * self.x + self.c) & self.m
        return self.x

class Feistel:
    """ Feistel cipher with Rijndael S-box as PRF. """
    SBOX = list(bytes.fromhex('637c777bf26b6fc53001672bfed7ab76ca82c97dfa5947f0add4a2af9ca472c0b7fd9326363ff7cc34a5e5f171d8311504c723c31896059a071280e2eb27b27509832c1a1b6e5aa0523bd6b329e32f8453d100ed20fcb15b6acbbe394a4c58cfd0efaafb434d338545f9027f503c9fa851a3408f929d38f5bcb6da2110fff3d2cd0c13ec5f974417c4a77e3d645d197360814fdc222a908846eeb814de5e0bdbe0323a0a4906245cc2d3ac629195e479e7c8376d8dd54ea96c56f4ea657aae08ba78252e1ca6b4c6e8dd741f4bbd8b8a703eb5664803f60e613557b986c11d9ee1f8981169d98e949b1e87e9ce5528df8ca1890dbfe6426841992d0fb054bb16'))

    def __init__(self, key: bytes, blockBits: int, rounds: int) -> None:
        assert not blockBits % 16
        assert len(key) >= 2 * (blockBits // 16)
        key = int.from_bytes(key, 'big')
        self.key = []
        for _ in range(2):
            self.key.append(key & (2 ** (blockBits // 2) - 1))
            key >>= blockBits // 2
        self.fullLen = blockBits
        self.halfLen = blockBits // 2
        self.fullAnd = 2 ** self.fullLen - 1
        self.halfAnd = 2 ** self.halfLen - 1
        self.rounds = rounds
        
    # Private methods
    
    def __F(self, x: int) -> int:
        """ Applies PRF. """
        x = ((x << (self.halfLen - 5)) | (x >> 5)) & self.halfAnd
        y = 0
        for _ in range(self.halfLen // 8):
            y <<= 8
            y |= self.SBOX[x & 0xff]
            x >>= 8
        return ((y >> (self.halfLen - 1)) | (y << 1)) & self.halfAnd
        
    def __KeySchedule(self) -> LCG:
        """ Returns PRNG object to generate key schedule. """
        return LCG(self.key[0], 1, self.key[1], self.halfLen)
    
    def __Pad(self, msg: bytes) -> int:
        """ Pads message until its length is a multiple of full length. """
        pbyt = b'\x01' + msg
        pint = int.from_bytes(pbyt, 'big')
        pint = (pint << 1) | 1
        plen = pint.bit_length() % self.fullLen
        if plen:
            pint <<= self.fullLen - plen
        return pint
        
    # Public methods
    
    def Encrypt(self, msg: bytes) -> bytes:
        """ Encrypts message using standard Feistel structure and LCG-based key schedule. """
        msg = self.__Pad(msg)
        blocks = []
        while msg:
            blocks.append(msg & self.fullAnd)
            msg >>= self.fullLen
        cip = 0
        roundKeys = self.__KeySchedule()
        for block in blocks[::-1]:
            li, ri = block >> self.halfLen, block & self.halfAnd
            for _ in range(self.rounds):
                lj, rj = li ^ self.__F(ri ^ roundKeys.Get()), ri
                li, ri = rj, lj
            cip <<= self.fullLen
            cip |= (lj << self.halfLen) | rj
        return cip.to_bytes(len(blocks) * self.fullLen // 8, 'big')

#------------------------------------------------------------------------------------------------------------------------------#
#   MAIN LOOP                                                                                                                  #
#------------------------------------------------------------------------------------------------------------------------------#
if __name__ == "__main__":

    # Challenge parameters
    FST_BITS = 96
    FST_ROUNDS = 11

    # Challenge setup
    key = os.urandom(FST_BITS // 8)
    fst = Feistel(key, FST_BITS, FST_ROUNDS)

    encFlag = B64Encode(AES.new((16 * key)[:16], AES.MODE_ECB).encrypt(pad(FLAG, 16)))

    HDR = """|
|    ____   ___   ___  __   __  ___     _     ___  ____ ___  ___  
|   |  _ \ / _ \ / _ \|  \ /  |/ _ \  _| |_  / _ \|  _ (   )/ _ \ 
|   | |_) ) |_| | |_| |   v   | | | |/     \| | | | |_) ) || |_| |
|   |  _ (|  _  |  _  | |\_/| | | | ( (| |) ) | | |  _ (| ||  _  |
|   | |_) ) | | | |_| | |   | | |_| |\_   _/| |_| | |_) ) || | | |
|   |____/|_| |_|\___/|_|   |_|\___/   |_|   \___/|____(___)_| |_|
|
|     flag = {cipher_flag_b64}
|"""
    print(HDR.format(encFlag))

    # Main
    OPS = ['Encrypt', 'Quit']
    TUI = "|\n|  Menu:\n|    " + "\n|    ".join('[' + i[0] + ']' + i[1:] for i in OPS) + "\n|"

    while True:
        try:

            print(TUI)
            choice = input('|  > ').lower()

            # [Q]uit
            if choice == 'q':
                print("|\n|  [~] Stay safe ~ !\n|")
                break

            elif choice == 'e':
                msg = B64Decode(input("|  > (B64) "))
                cip = B64Encode(fst.Encrypt(msg))
                print("|\n|  [~] {}".format(cip))

            else:
                print("|\n|  [!] Invalid choice.")

        except KeyboardInterrupt:
            print("\n|\n|  [~] Stay safe ~ !\n|")
            break

        except Exception as e:

            print('|\n|  [!] ERROR: {}'.format(e))
