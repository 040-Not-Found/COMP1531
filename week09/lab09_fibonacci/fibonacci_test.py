import pytest
from fibonacci import generate

def test_sucess():
    assert generate(6) == [0, 1, 1, 2, 3, 5]

def test_n_less_than_one():
    assert generate(0) == []

