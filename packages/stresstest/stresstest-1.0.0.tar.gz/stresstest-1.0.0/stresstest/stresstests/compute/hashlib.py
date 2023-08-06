import hashlib
import math
import random

from stresstest.stresstest import BaseStresstest, Parameter


class Sha1Stresstest(BaseStresstest):
    name = ["compute", "hashlib", "Sha1Stresstest"]

    parameters = [Parameter("iterations", default=10000, type=int)]

    def run_test(self, iterations: int):
        with self:
            for i in range(iterations):
                content = bytearray(random.getrandbits(8) for _ in range(256))
                hashlib.sha1(content).hexdigest()


class Sha224Stresstest(BaseStresstest):
    name = ["compute", "hashlib", "Sha224Stresstest"]

    parameters = [Parameter("iterations", default=10000, type=int)]

    def run_test(self, iterations: int):
        with self:
            for i in range(iterations):
                content = bytearray(random.getrandbits(8) for _ in range(256))
                hashlib.sha224(content).hexdigest()


class Sha256Stresstest(BaseStresstest):
    name = ["compute", "hashlib", "Sha256Stresstest"]

    parameters = [Parameter("iterations", default=10000, type=int)]

    def run_test(self, iterations: int):
        with self:
            for i in range(iterations):
                content = bytearray(random.getrandbits(8) for _ in range(256))
                hashlib.sha256(content).hexdigest()


class Sha384Stresstest(BaseStresstest):
    name = ["compute", "hashlib", "Sha384Stresstest"]

    parameters = [Parameter("iterations", default=10000, type=int)]

    def run_test(self, iterations: int):
        with self:
            for i in range(iterations):
                content = bytearray(random.getrandbits(8) for _ in range(256))
                hashlib.sha384(content).hexdigest()


class Sha512Stresstest(BaseStresstest):
    name = ["compute", "hashlib", "Sha512Stresstest"]

    parameters = [Parameter("iterations", default=10000, type=int)]

    def run_test(self, iterations: int):
        with self:
            for i in range(iterations):
                content = bytearray(random.getrandbits(8) for _ in range(256))
                hashlib.sha512(content).hexdigest()


class Sha3Stresstest(BaseStresstest):
    name = ["compute", "hashlib", "Sha3Stresstest"]

    parameters = [Parameter("iterations", default=10000, type=int)]

    def run_test(self, iterations: int):
        with self:
            for i in range(iterations):
                content = bytearray(random.getrandbits(8) for _ in range(256))
                hashlib.sha3_256(content).hexdigest()
