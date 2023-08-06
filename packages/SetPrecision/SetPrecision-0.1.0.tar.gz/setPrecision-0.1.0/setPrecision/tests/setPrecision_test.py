from ..setPrecision import set


def test_setPrecisionA() -> None:
    assert set(3.1415926, 3) == '3.142'


def test_setPrecisionB() -> None:
    assert set(10.5, 0) == '10'


def test_setPrecisionC() -> None:
    assert set(5280.40836894, 2) == '5280.41'


def test_setPrecisionD() -> None:
    assert set(150, 5) == '150.00000'


def test_setPrecisionE() -> None:
    assert set(1485809.4861172) == '1485809.5'
