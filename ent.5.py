#relat


class IdadeInvalidaError(Exception):
    pass


def validar_idade(idade):
    if idade < 0 or idade > 120:
        raise IdadeInvalidaError(
            "Idade fora do intervalo permitido (0 a 120)."
        )


dados = ["18", "25", "-5", "abc", "150", "32", "0"]

validos = []
invalidos = []

for registro in dados:
    try:
        idade = int(registro)
        validar_idade(idade)
        validos.append(idade)

    except ValueError:
        invalidos.append(
            (registro, "Valor não é um número inteiro")
        )

    except IdadeInvalidaError as erro:
        invalidos.append((registro, str(erro)))


# Estatísticas da análise
total = len(dados)
quant_validos = len(validos)
quant_invalidos = len(invalidos)

percentual_validos = (
    quant_validos / total * 100 if total else 0
)

media_idades = (
    sum(validos) / quant_validos if quant_validos else 0
)


# Relatório formatado com f-strings
print("\n" + "=" * 45)
print("         RELATÓRIO DE VALIDAÇÃO")
print("=" * 45)

print(f"Total de registros:       {total}")
print(f"Registros válidos:        {quant_validos}")
print(f"Registros inválidos:      {quant_invalidos}")
print(f"Percentual de aprovação:  {percentual_validos:.2f}%")
print(f"Média das idades válidas: {media_idades:.2f}")

print("\n--- DADOS VÁLIDOS ---")
if validos:
    for idade in validos:
        print(f"Idade: {idade} anos")
else:
    print("Nenhum registro válido.")

print("\n--- DADOS INVÁLIDOS ---")
if invalidos:
    for valor, motivo in invalidos:
        print(f"Valor: {valor} | Motivo: {motivo}")
else:
    print("Nenhum registro inválido.")

print("=" * 45)
print("Análise finalizada.")