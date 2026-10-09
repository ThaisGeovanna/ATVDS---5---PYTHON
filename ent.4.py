# atvd 4


class IdadeInvalidaError(Exception):
    """Exceção personalizada para idade inválida."""
    pass


def verificar_idade(idade):
    if idade < 0 or idade > 120:
        raise IdadeInvalidaError(
            "A idade deve estar entre 0 e 120 anos."
        )

    print(f"Idade válida: {idade} anos.")


try:
    idade = int(input("Digite sua idade: "))
    verificar_idade(idade)

except ValueError:
    print("Erro: digite um número inteiro.")

except IdadeInvalidaError as erro:
    print(f"Erro personalizado: {erro}")

else:
    print("Verificação realizada com sucesso!")

finally:
    print("Programa finalizado.")