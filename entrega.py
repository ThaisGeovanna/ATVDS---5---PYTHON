#py1

#!/usr/bin/env python3
"""
principal.py - Lê um arquivo CSV ou TXT com e-mail, CPF, telefone e data,
extrai e valida cada campo e gera um relatório.

Uso:
    python principal.py dados.csv
    python principal.py dados.txt --saida resultado.csv
"""

import argparse
import csv
import re
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------- Regex
RE_EMAIL = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
RE_CPF = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")
RE_TELEFONE = re.compile(
    r"(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)(?:9\s?)?\d{4}[-\s]?\d{4}"
)
RE_DATA = re.compile(r"\b(?:\d{2}[/\-]\d{2}[/\-]\d{4}|\d{4}-\d{2}-\d{2})\b")

FORMATOS_DATA = ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d")


# ---------------------------------------------------------------- Validadores
def validar_email(email: str) -> bool:
    return bool(RE_EMAIL.fullmatch(email))


def validar_cpf(cpf: str) -> bool:
    numeros = re.sub(r"\D", "", cpf)
    if len(numeros) != 11 or numeros == numeros[0] * 11:
        return False
    for i in (9, 10):
        soma = sum(int(numeros[j]) * (i + 1 - j) for j in range(i))
        digito = (soma * 10 % 11) % 10
        if digito != int(numeros[i]):
            return False
    return True


def formatar_cpf(cpf: str) -> str:
    n = re.sub(r"\D", "", cpf)
    return f"{n[:3]}.{n[3:6]}.{n[6:9]}-{n[9:]}"


def validar_telefone(telefone: str) -> bool:
    n = re.sub(r"\D", "", telefone)
    if n.startswith("55") and len(n) in (12, 13):
        n = n[2:]
    if len(n) not in (10, 11):
        return False
    if n[0] == "0" or n[1] == "0":  # DDD inválido
        return False
    if len(n) == 11 and n[2] != "9":  # celular começa com 9
        return False
    return True


def formatar_telefone(telefone: str) -> str:
    n = re.sub(r"\D", "", telefone)
    if n.startswith("55") and len(n) in (12, 13):
        n = n[2:]
    if len(n) == 11:
        return f"({n[:2]}) {n[2:7]}-{n[7:]}"
    if len(n) == 10:
        return f"({n[:2]}) {n[2:6]}-{n[6:]}"
    return telefone


def interpretar_data(texto: str):
    for fmt in FORMATOS_DATA:
        try:
            return datetime.strptime(texto, fmt).date()
        except ValueError:
            continue
    return None


# ---------------------------------------------------------------- Extração
def extrair_campos(texto: str) -> dict:
    """Extrai o primeiro e-mail, CPF, telefone e data encontrados no texto."""
    email = RE_EMAIL.search(texto)
    cpf = RE_CPF.search(texto)
    texto_sem_cpf = texto.replace(cpf.group(), " ") if cpf else texto
    data = RE_DATA.search(texto_sem_cpf)
    texto_sem_data = texto_sem_cpf.replace(data.group(), " ") if data else texto_sem_cpf
    telefone = RE_TELEFONE.search(texto_sem_data)
    return {
        "email": email.group() if email else "",
        "cpf": cpf.group() if cpf else "",
        "telefone": telefone.group().strip() if telefone else "",
        "data": data.group() if data else "",
    }


def ler_arquivo(caminho: Path):
    """Lê CSV (com cabeçalho ou não) ou TXT e devolve lista de dicts."""
    registros = []
    if caminho.suffix.lower() == ".csv":
        with caminho.open(encoding="utf-8-sig", newline="") as f:
            amostra = f.read(2048)
            f.seek(0)
            try:
                dialeto = csv.Sniffer().sniff(amostra, delimiters=",;\t|")
            except csv.Error:
                dialeto = csv.excel
            leitor = csv.reader(f, dialeto)
            for linha in leitor:
                if not any(c.strip() for c in linha):
                    continue
                registros.append(extrair_campos(" ; ".join(linha)))
    else:
        with caminho.open(encoding="utf-8-sig") as f:
            for linha in f:
                if linha.strip():
                    registros.append(extrair_campos(linha))
    # Descarta linha de cabeçalho (sem nenhum campo reconhecido)
    return [r for r in registros if any(r.values())]


# ---------------------------------------------------------------- Processamento
def processar(registros):
    resultado = []
    for i, r in enumerate(registros, start=1):
        data = interpretar_data(r["data"]) if r["data"] else None
        item = {
            "linha": i,
            "email": r["email"],
            "email_valido": validar_email(r["email"]) if r["email"] else False,
            "cpf": formatar_cpf(r["cpf"]) if r["cpf"] else "",
            "cpf_valido": validar_cpf(r["cpf"]) if r["cpf"] else False,
            "telefone": formatar_telefone(r["telefone"]) if r["telefone"] else "",
            "telefone_valido": validar_telefone(r["telefone"]) if r["telefone"] else False,
            "data": data.strftime("%d/%m/%Y") if data else r["data"],
            "data_valida": data is not None,
        }
        resultado.append(item)
    return resultado


def imprimir_relatorio(resultado):
    total = len(resultado)
    print(f"\n{'=' * 70}\nRELATÓRIO DE VALIDAÇÃO — {total} registro(s)\n{'=' * 70}")
    for item in resultado:
        def marca(ok):
            return "OK " if ok else "ERRO"
        print(
            f"[{item['linha']:>3}] "
            f"E-mail: {item['email'] or '-':<30} {marca(item['email_valido'])} | "
            f"CPF: {item['cpf'] or '-':<14} {marca(item['cpf_valido'])} | "
            f"Tel: {item['telefone'] or '-':<15} {marca(item['telefone_valido'])} | "
            f"Data: {item['data'] or '-':<10} {marca(item['data_valida'])}"
        )
    print("-" * 70)
    for campo in ("email", "cpf", "telefone", "data"):
        chave = f"{campo}_valido" if campo != "data" else "data_valida"
        validos = sum(1 for r in resultado if r[chave])
        print(f"{campo.capitalize():<9}: {validos}/{total} válidos")
    print()


def salvar_csv(resultado, caminho: Path):
    if not resultado:
        return
    with caminho.open("w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=resultado[0].keys())
        escritor.writeheader()
        escritor.writerows(resultado)
    print(f"Resultado salvo em: {caminho}")


# ---------------------------------------------------------------- Main
def main():
    parser = argparse.ArgumentParser(
        description="Lê CSV/TXT com e-mail, CPF, telefone e data e valida os campos."
    )
    parser.add_argument("arquivo", help="Caminho do arquivo .csv ou .txt")
    parser.add_argument("--saida", help="Salva o resultado em um CSV", default=None)
    args = parser.parse_args()

    caminho = Path(args.arquivo)
    if not caminho.is_file():
        sys.exit(f"Arquivo não encontrado: {caminho}")
    if caminho.suffix.lower() not in (".csv", ".txt"):
        sys.exit("Formato não suportado. Use .csv ou .txt.")

    registros = ler_arquivo(caminho)
    if not registros:
        sys.exit("Nenhum dado reconhecido no arquivo.")

    resultado = processar(registros)
    imprimir_relatorio(resultado)
    if args.saida:
        salvar_csv(resultado, Path(args.saida))


if __name__ == "__main__":
    main()