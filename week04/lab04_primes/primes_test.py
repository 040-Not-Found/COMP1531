from primes import factors

def test_primes():
    assert factors(16) == [2, 2, 2, 2]
    assert factors(21) == [3, 7]
    assert factors(1) == []
