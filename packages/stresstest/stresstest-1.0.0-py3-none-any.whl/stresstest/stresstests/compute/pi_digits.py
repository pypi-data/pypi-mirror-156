import random

from stresstest.stresstest import BaseStresstest, Parameter


class CalculatePiDigitsStresstest(BaseStresstest):
    name = ["compute", "pi_digits", "CalculatePiDigitsStresstest"]

    parameters = [Parameter("iterations", default=10000000, type=int)]

    def run_test(self, iterations: int):
        pi = 0

        with self:
            for i in range(iterations):
                pi += 4 * (1 - (i % 2) * 2) / (2 * i + 1)


class PiDigitsMonteCarloStresstest(BaseStresstest):
    name = ["compute", "pi_digits", "PiDigitsMonteCarloStresstest"]

    parameters = [Parameter("iterations", default=10000000, type=int)]

    def run_test(self, iterations: int):
        pi = 0

        with self:
            for i in range(iterations):
                x = random.random()
                y = random.random()
                if x * x + y * y < 1:
                    pi += 1
            pi = pi / iterations * 4
