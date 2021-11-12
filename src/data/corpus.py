from typing import List


class DataLoader:
    def load_data(self) -> List[str]:
        raise NotImplementedError()

    @classmethod
    def tokenize(cls, data: List[str], lower_case: bool) -> List[List[str]]:
        return [[el.lower() if lower_case else el for el in document.split()] for document in data]


class DummyLoader(DataLoader):
    def __init__(self) -> None:
        self.data = self.load_data()

    def load_data(self) -> List[str]:
        return [
            "Document one is about Barack Obama",
            "The second document is critizing Trump",
            "The third document is about Apple",
        ]

    def get_data(self) -> List[str]:
        return self.data
