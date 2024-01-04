'''
Tests for check_password()
'''
from password import check_password
def test_strong():
    assert check_password('SJelfqwerty123') == 'Strong password'
def test_moderate():
    assert check_password('asdfghjkl123') == 'Moderate password'
    
def test_poor():
    assert check_password('wdNmd') == 'Poor password'

def test_horrible():
    assert check_password('password') == 'Horrible password'
    assert check_password('123456') == 'Horrible password'

