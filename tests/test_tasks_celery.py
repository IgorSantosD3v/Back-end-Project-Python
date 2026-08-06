from tasks import somar, fatorial

def test_somar():
    assert somar(2, 3) == 5

def test_fatorial():
    assert fatorial(5) == 120

def test_fatorial_zero():
    assert fatorial(0) == 1