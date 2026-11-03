import sqlite3

import pytest

from etl.pipeline import ejecutar_pipeline
from etl.reportes import buscar_cliente, evaluar_regla, total


@pytest.fixture
def conexion():
    con = sqlite3.connect(":memory:")
    yield con
    con.close()


def _csv(tmp_path, contenido, nombre="clientes.csv"):
    ruta = tmp_path / nombre
    ruta.write_text(contenido)
    return ruta


def test_pipeline_carga_clientes(conexion, tmp_path):
    csv = _csv(tmp_path, "id,email\n1, Ana@Mail.com\n2,luis@mail.com\n")
    assert ejecutar_pipeline(csv, conexion) == 2
    filas = conexion.execute(
        "SELECT email FROM clientes ORDER BY id").fetchall()
    assert filas == [("ana@mail.com",), ("luis@mail.com",)]


def test_pipeline_es_idempotente(conexion, tmp_path):
    csv = _csv(tmp_path, "id,email\n1,ana@mail.com\n2,luis@mail.com\n")
    ejecutar_pipeline(csv, conexion)
    ejecutar_pipeline(csv, conexion)
    cantidad = conexion.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
    assert cantidad == 2  # no 4


def test_pipeline_email_invalido_falla_y_no_carga_nada(conexion, tmp_path):
    # Decisión: todo o nada. Un email inválido aborta la carga completa.
    csv = _csv(tmp_path, "id,email\n1,ana@mail.com\n2,esto-no-es-email\n")
    with pytest.raises(ValueError):
        ejecutar_pipeline(csv, conexion)
    cantidad = conexion.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
    assert cantidad == 0


def test_reconciliacion_origen_destino(conexion, tmp_path):
    csv = _csv(tmp_path, "id,email\n1,a@m.com\n2,b@m.com\n3,c@m.com\n")
    cargadas = ejecutar_pipeline(csv, conexion)
    en_bd = conexion.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
    assert cargadas == en_bd == 3


# ---- reportes.py (versión corregida) ----
@pytest.fixture
def con_datos(conexion, tmp_path):
    csv = _csv(tmp_path, "id,email\n1,ana@mail.com\n2,luis@mail.com\n")
    ejecutar_pipeline(csv, conexion)
    return conexion


def test_buscar_cliente_existente(con_datos):
    assert buscar_cliente(con_datos, "ana@mail.com") == [(1, "ana@mail.com")]


def test_buscar_cliente_resiste_inyeccion_sql(con_datos):
    assert buscar_cliente(con_datos, "' OR '1'='1") == []


def test_evaluar_regla_valida():
    assert evaluar_regla((0, ">", 5), (10, "a@b.com")) is True
    assert evaluar_regla((0, "==", 5), (10, "a@b.com")) is False


def test_evaluar_regla_no_ejecuta_codigo():
    with pytest.raises(ValueError):
        evaluar_regla((0, "__import__('os').system('ls')", 1), (1, "x"))


def test_total_suma_segunda_columna():
    assert total([("a", 1), ("b", 2)]) == 3


def test_total_con_datos_invalidos_lanza_error():
    with pytest.raises(ValueError):
        total([("a", "no-numero"), ("b", 2)])
