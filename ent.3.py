import csv

ARQUIVO = "dados.csv"

try:
    # utf-8-sig remove o caractere invisível (BOM) que o Excel coloca no início
    with open(ARQUIVO, newline="", encoding="utf-8-sig") as arquivo:
        # Detecta automaticamente se o separador é ; ou ,
        amostra = arquivo.read(2048)
        arquivo.seek(0)
        try:
            separador = csv.Sniffer().sniff(amostra, delimiters=";,").delimiter
        except csv.Error:
            separador = ";"

        leitor = csv.DictReader(arquivo, delimiter=separador)

        # Normaliza os nomes das colunas: sem espaços e em minúsculas
        leitor.fieldnames = [c.strip().lower() for c in (leitor.fieldnames or [])]
        colunas = leitor.fieldnames

        print("Separador detectado:", repr(separador))
        print("Colunas encontradas:", colunas)

        for obrigatoria in ("nome", "idade"):
            if obrigatoria not in colunas:
                raise KeyError(f"A coluna '{obrigatoria}' não existe no CSV.")

        for linha in leitor:
            nome = linha["nome"].strip()
            idade = int(linha["idade"])
            print(f"Nome: {nome} | Idade: {idade}")

except FileNotFoundError:
    print("Erro: o arquivo dados.csv não foi encontrado.")

except ValueError:
    print("Erro: a idade precisa ser um número inteiro.")

except KeyError as erro:
    print(f"Erro: coluna ausente no CSV: {erro}")

else:
    print("Arquivo lido e processado com sucesso!")