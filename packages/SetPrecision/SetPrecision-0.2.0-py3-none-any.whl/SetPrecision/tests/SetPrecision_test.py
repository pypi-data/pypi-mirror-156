from ..SetPrecision import set_precision


def test_setPrecisionA() -> None:
    assert set_precision(3.1415926, 3) == '3.142'


def test_setPrecisionB() -> None:
    assert set_precision(10.5, 0) == '10'


def test_setPrecisionC() -> None:
    assert set_precision(5280.40836894, 2) == '5280.41'


def test_setPrecisionD() -> None:
    assert set_precision(150, 5) == '150.00000'


def test_setPrecisionE() -> None:
    assert set_precision(1485809.4861172) == '1485809.5'
