# MIT License
#
# Copyright (c) 2022 Mark Qvist / unsigned.io
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
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

import os
import time

from RNS.Cryptography import HMAC
from RNS.Cryptography import PKCS7
from RNS.Cryptography.AES import AES_128_CBC

class Fernet():
    FERNET_VERSION            = 0x80
    FERNET_OVERHEAD           = 57          # In bytes
    OPTIMISED_FERNET_OVERHEAD = 54          # In bytes

    @staticmethod
    def generate_key():
        return os.urandom(32)

    def __init__(self, key = None):
        if key == None:
            raise ValueError("Fernet key cannot be None")

        if len(key) != 32:
            raise ValueError("Fernet key must be 32 bytes, not "+str(len(key)))
            
        self._signing_key = key[:16]
        self._encryption_key = key[16:]


    def verify_hmac(self, token):
        if len(token) <= 32:
            raise ValueError("Cannot verify HMAC on token of only "+str(len(token))+" bytes")
        else:
            received_hmac = token[-32:]
            expected_hmac = HMAC.new(self._signing_key, token[:-32]).digest()

            if received_hmac == expected_hmac:
                return True
            else:
                return False


    def encrypt(self, data = None):
        iv = os.urandom(16)
        current_time = int(time.time())

        if not isinstance(data, bytes):
            raise TypeError("Fernet token plaintext input must be bytes")

        ciphertext = AES_128_CBC.encrypt(
            plaintext = PKCS7.pad(data),
            key = self._encryption_key,
            iv = iv,
        )

        signed_parts = b"\x80"+current_time.to_bytes(length=8, byteorder="big")+iv+ciphertext

        return signed_parts + HMAC.new(self._signing_key, signed_parts).digest()


    def decrypt(self, token = None):
        if not isinstance(token, bytes):
            raise TypeError("Fernet token must be bytes")

        if not self.verify_hmac(token):
            raise ValueError("Fernet token HMAC was invalid")

        iv = token[9:25]
        ciphertext = token[25:-32]

        try:
            plaintext = PKCS7.unpad(
                AES_128_CBC.decrypt(
                    ciphertext,
                    self._encryption_key,
                    iv,
                )
            )

            return plaintext

        except Exception as e:
            raise ValueError("Could not decrypt Fernet token")