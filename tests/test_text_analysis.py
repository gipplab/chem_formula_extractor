from typing import List
import pytest

from src.modules.text_analysis import extract_n_grams


@pytest.mark.parametrize(
    "documents, n, expected",
    [
        (
            [["the", "fox", "jumps", "over", "the"]],
            2,
            set(["the fox", "fox jumps", "jumps over", "over the"]),
        ),
        (
            [["only", "two", "only", "two"]],
            2,
            set(["only two", "two only"]),
        ),
        (
            [["must", "be", "one"]],
            3,
            set(["must be one"]),
        ),
    ],
)
def test_extract_n_grams(documents: List[List[str]], n: int, expected: List[str]) -> None:
    # Testing the function extract_n_grams
    assert extract_n_grams(documents, n) == expected
