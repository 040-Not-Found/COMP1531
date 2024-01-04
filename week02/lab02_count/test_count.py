from count import count_char

def test_empty():
    assert count_char("") == '{}'

def test_simple():
    assert count_char("abc") == "{'a': 1, 'b': 1, 'c': 1}"

def test_double():
    assert count_char("aa") == "{'a': 2}"
    
def test_mix():
    assert count_char("Helloooo") == "{'H': 1, 'e': 1, 'l': 2, 'o': 4}"
