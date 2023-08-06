import math

from stresstest.stresstest import BaseStresstest, Parameter


class FactorizeNNumbersStresstest(BaseStresstest):
    name = ["compute", "factorization", "FactorizeNNumbersStresstest"]

    parameters = [Parameter("n_numbers", default=100000, type=int)]

    def run_test(self, n_numbers: int):
        with self:
            for i in range(n_numbers):
                _ = list(self.factors(i))

    def factors(self, n):
        j = 2
        while n > 1:
            for i in range(j, int(math.sqrt(n + 0.05)) + 1):
                if n % i == 0:
                    n /= i
                    j = i
                    yield i
                    break
            else:
                if n > 1:
                    yield n
                    break
