import pytest
from src.data.corpus import DataLoader, DummyLoader


def test_corpus_loader() -> None:
    # Testing the DataLoader class
    base_loader = DataLoader()
    corpus = DummyLoader()

    with pytest.raises(NotImplementedError):
        base_loader.load_data()

    assert corpus is not None
    assert len(corpus.get_data()) == 3

    tokenized_documents = DataLoader.tokenize(corpus.get_data(), lower_case=True)
    for tokenized_document in tokenized_documents:
        assert len(tokenized_document) == 6
        for token in tokenized_document:
            assert token.islower()
