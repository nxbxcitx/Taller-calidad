import pytest

from etl.transform import calcular_total, normalizar_email


@pytest.mark.parametrize("entrada, esperado", [
    (" Ana@Mail.COM ", "ana@mail.com"),
    ("luis.p+datos@uni.edu.co", "luis.p+datos@uni.edu.co"),
    ("MARIA@EMPRESA.COM", "maria@empresa.com"),
])
def test_normalizar_email_valido(entrada, esperado):
    assert normalizar_email(entrada) == esperado


@pytest.mark.parametrize("entrada", ["", " ", "sin-arroba", None, 123, "a@b"])
def test_normalizar_email_invalido(entrada):
    with pytest.raises(ValueError):
        normalizar_email(entrada)


@pytest.mark.parametrize("precio, cantidad, descuento, esperado", [
    (10, 3, 0.0, 30.0),      # sin descuento
    (100, 2, 0.25, 150.0),   # descuento normal
    (50, 1, 1, 0.0),         # límite: descuento 1
    (50, 0, 0.5, 0.0),       # límite: cantidad 0
    (19.99, 3, 0.0, 59.97),  # redondeo a 2 decimales
    (10, 1, 0.333, 6.67),    # redondeo con descuento
])
def test_calcular_total_valido(precio, cantidad, descuento, esperado):
    assert calcular_total(precio, cantidad, descuento) == esperado


def test_calcular_total_descuento_por_defecto():
    assert calcular_total(5, 4) == 20.0


@pytest.mark.parametrize("precio, cantidad, descuento", [
    (-1, 1, 0),     # precio negativo
    (1, -1, 0),     # cantidad negativa
    (1, 1, 1.5),    # descuento > 1
    (1, 1, -0.1),   # descuento negativo
])
def test_calcular_total_invalido(precio, cantidad, descuento):
    with pytest.raises(ValueError):
        calcular_total(precio, cantidad, descuento)
