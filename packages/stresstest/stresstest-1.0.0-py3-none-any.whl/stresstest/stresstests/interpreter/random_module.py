from stresstest.stresstest import BaseStresstest, Parameter


class RandomIntegerGeneratorStresstest(BaseStresstest):
    name = ["interpreter", "random_module", "RandomIntegerGeneratorStresstest"]

    parameters = [Parameter("iterations", default=50000, type=int)]

    def run_test(self, iterations: int):
        import random

        with self:
            for _ in range(iterations):
                random.randint(0, 100)


class RandomNumberGeneratorStresstest(BaseStresstest):
    name = ["interpreter", "random_module", "RandomNumberGeneratorStresstest"]

    parameters = [Parameter("iterations", default=50000, type=int)]

    def run_test(self, iterations: int):
        import random

        with self:
            for _ in range(iterations):
                random.random()


class SortIntegersStresstest(BaseStresstest):
    name = ["interpreter", "random_module", "SortIntegersStresstest"]

    parameters = [Parameter("list_length", default=1000000, type=int)]

    def run_test(self, list_length: int):
        import random

        integers_list = [random.randint(0, 100) for _ in range(list_length)]

        with self:
            _ = sorted(integers_list)
