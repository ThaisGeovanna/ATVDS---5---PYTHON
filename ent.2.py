# valis

"""
Validação de formato de campos com expressões regulares (módulo `re`).

Campos: e-mail, CPF, telefone (Brasil) e data (dd/mm/aaaa).
"""

import re
from datetime import datetime

# ---------------------------------------------------------------------------
# Padrões (compilados uma única vez)
# ---------------------------------------------------------------------------

# E-mail: parte local (\w, ".", "+", "-") + "@" + domínio com pelo menos um
# ponto e TLD de 2+ letras. Ex.: ana.silva+teste@empresa.com.br
PADRAO_EMAIL = re.compile(
    r"^[\w.+-]+"                # parte local
    r"@"
    r"[A-Za-z0-9-]+"            # primeiro rótulo do domínio
    r"(?:\.[A-Za-z0-9-]+)*"     # rótulos intermediários (opcional)
    r"\.[A-Za-z]{2,}$",         # TLD
    re.ASCII,
)

# CPF: 000.000.000-00 (formatado) OU 00000000000 (somente dígitos).
PADRAO_CPF = re.compile(r"^(?:\d{3}\.\d{3}\.\d{3}-\d{2}|\d{11})$")

# Telefone brasileiro, com ou sem DDI/DDD/máscara. Exemplos aceitos:
#   (11) 91234-5678 | (11) 1234-5678 | 11912345678 | +55 11 91234-5678
PADRAO_TELEFONE = re.compile(
    r"^(?:\+55\s?)?"            # DDI opcional
    r"(?:\(?[1-9]\d\)?\s?)"     # DDD (2 dígitos, não começa com 0)
    r"(?:9\d{4}|\d{4})"         # 9 dígitos (celular) ou 8 (fixo): 1ª parte
    r"-?\d{4}$"                 # hífen opcional + 4 últimos dígitos
)

# Data dd/mm/aaaa com dia 01-31 e mês 01-12 (o calendário real é checado à parte).
PADRAO_DATA = re.compile(
    r"^(0[1-9]|[12]\d|3[01])"   # dia
    r"/(0[1-9]|1[0-2])"         # mês
    r"/(\d{4})$"                # ano
)


# ---------------------------------------------------------------------------
# Funções de validação
# ---------------------------------------------------------------------------

def validar_email(email: str) -> bool:
    """Retorna True se o texto tiver formato de e-mail válido."""
    return bool(PADRAO_EMAIL.fullmatch(email.strip()))


def validar_cpf(cpf: str, verificar_digitos: bool = False) -> bool:
    """
    Valida o formato do CPF. Com `verificar_digitos=True`, confere também
    os dígitos verificadores (e rejeita sequências repetidas como 111.111.111-11).
    """
    cpf = cpf.strip()
    if not PADRAO_CPF.fullmatch(cpf):
        return False
    if not verificar_digitos:
        return True

    numeros = re.sub(r"\D", "", cpf)  # remove tudo que não é dígito
    if numeros == numeros[0] * 11:
        return False
    for tamanho in (9, 10):
        soma = sum(int(d) * peso
                   for d, peso in zip(numeros[:tamanho], range(tamanho + 1, 1, -1)))
        digito = (soma * 10 % 11) % 10
        if digito != int(numeros[tamanho]):
            return False
    return True


def validar_telefone(telefone: str) -> bool:
    """Retorna True se o texto tiver formato de telefone brasileiro válido."""
    return bool(PADRAO_TELEFONE.fullmatch(telefone.strip()))


def validar_data(data: str, checar_calendario: bool = True) -> bool:
    """
    Valida data no formato dd/mm/aaaa. Com `checar_calendario=True`,
    rejeita datas inexistentes (ex.: 31/02/2024).
    """
    data = data.strip()
    if not PADRAO_DATA.fullmatch(data):
        return False
    if not checar_calendario:
        return True
    try:
        datetime.strptime(data, "%d/%m/%Y")
        return True
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# Testes rápidos
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    casos = [
        ("e-mail", validar_email, [
            ("ana.silva+teste@empresa.com.br", True),
            ("joao_123@gmail.com", True),
            ("sem-arroba.com", False),
            ("a@b", False),
            ("usuario@dominio..com", False),
        ]),
        ("CPF", validar_cpf, [
            ("123.456.789-09", True),
            ("12345678909", True),
            ("123.456.789-0", False),
            ("123456789-09", False),
            ("abc.def.ghi-jk", False),
        ]),
        ("telefone", validar_telefone, [
            ("(11) 91234-5678", True),
            ("(11) 1234-5678", True),
            ("11912345678", True),
            ("+55 11 91234-5678", True),
            ("(01) 91234-5678", False),
            ("91234-5678", False),
        ]),
        ("data", validar_data, [
            ("09/10/2026", True),
            ("29/02/2024", True),
            ("31/02/2024", False),
            ("32/01/2024", False),
            ("2024-10-09", False),
        ]),
    ]

    total = erros = 0
    for campo, funcao, entradas in casos:
        print(f"\n== {campo} ==")
        for valor, esperado in entradas:
            obtido = funcao(valor)
            ok = obtido == esperado
            total += 1
            erros += not ok
            print(f"  [{'OK' if ok else 'FALHOU'}] {valor!r:38} -> {obtido}")

    print(f"\n{total - erros}/{total} testes passaram.")

    # Dígitos verificadores do CPF (opcional)
    print("\nCPF com dígitos verificadores:")
    print("  529.982.247-25 ->", validar_cpf("529.982.247-25", verificar_digitos=True))
    print("  111.111.111-11 ->", validar_cpf("111.111.111-11", verificar_digitos=True))