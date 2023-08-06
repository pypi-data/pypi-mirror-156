from stresstest.stresstest import BaseStresstest, Parameter


class CreateLargeDictionaryFromListStresstest(BaseStresstest):
    name = ["interpreter", "dict_class", "CreateLargeDictionaryFromListStresstest"]

    parameters = [Parameter("list_length", default=1000000, type=int)]

    def run_test(self, list_length: int):
        import random

        source_list = [(random.random(), random.random()) for _ in range(list_length)]

        with self:
            _ = dict(source_list)


class DictionaryRandomAccessStresstest(BaseStresstest):
    name = ["interpreter", "dict_class", "DictionaryRandomAccessStresstest"]

    parameters = [Parameter("list_length", default=1000000, type=int)]

    def run_test(self, list_length: int):
        import random

        source_list = [(random.random(), random.random()) for _ in range(list_length)]
        keys = [x[0] for x in source_list]
        random.shuffle(keys)
        test_dict = dict(source_list)

        with self:
            for key in keys:
                _ = test_dict[key]


class DictionarySequentialAccessStresstest(BaseStresstest):
    name = ["interpreter", "dict_class", "DictionarySequentialAccessStresstest"]

    parameters = [Parameter("list_length", default=1000000, type=int)]

    def run_test(self, list_length: int):
        import random

        source_list = [(random.random(), random.random()) for _ in range(list_length)]
        keys = [x[0] for x in source_list]
        test_dict = dict(source_list)

        with self:
            for key in keys:
                _ = test_dict[key]
