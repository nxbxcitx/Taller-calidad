import operator
import os

# Credencial tomada de variable de entorno, nunca escrita en el código.
DB_PASSWORD = os.environ.get("DB_PASSWORD")

OPERADORES = {
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
}


def buscar_cliente(con, email):
    # Consulta parametrizada: el valor nunca se concatena al SQL.
    consulta = "SELECT * FROM clientes WHERE email = ?"
    return con.execute(consulta, (email,)).fetchall()


def evaluar_regla(regla, fila):
    """Evalúa una regla (indice, operador, valor) sin usar eval.

    Ejemplo: evaluar_regla((0, ">", 5), (10, "a@b.com")) -> True
    """
    indice, op, valor = regla
    if op not in OPERADORES:
        raise ValueError(f"operador no permitido: {op}")
    return OPERADORES[op](fila[indice], valor)


def total(filas):
    try:
        return sum(f[1] for f in filas)
    except (TypeError, IndexError) as exc:
        raise ValueError("filas con formato inválido") from exc