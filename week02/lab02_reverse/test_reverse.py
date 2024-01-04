'''
Tests for reverse_words()
'''
from reverse import reverse_words
def test_reverse():
    l = ["super", "junior"]
    reverse_words(l)
    assert l == ["junior", "super"]
    
    l = ["neo", "culture", "techology"]
    reverse_words(l)
    assert l  == ["techology", "culture", "neo"]
    
    l = ["1", "2"]
    reverse_words(l)
    assert l == ["2", "1"]
    
    l = ["B", "A", "D"]
    reverse_words(l)
    assert l == ["D", "A", "B"]
    
    l = ["&", "*"]
    reverse_words(l)
    assert l == ["*", "&"]
