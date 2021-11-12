from typing import List, Set


def extract_n_grams(tokenized_documents: List[List[str]], n: int) -> Set[str]:
    """
    Extracts n-grams from a list of tokenized documents.

    :param tokenized_documents: List of tokenized documents.
    :param n: The n-gram size.
    :return: List of n-grams.
    """
    n_grams = []
    for document in tokenized_documents:
        print(document)
        print(n)
        for i in range(len(document) - n + 1):
            n_grams.append(" ".join(document[i : i + n]))
    return set(n_grams)
