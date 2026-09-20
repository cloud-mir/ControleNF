import json
import os


# ============================================================
# CONFIGURAÇÃO DO ARQUIVO
# ============================================================

PASTA_CONTROLE_NF = os.path.dirname(os.path.abspath(__file__))

ARQUIVO = os.path.join(
    PASTA_CONTROLE_NF,
    "regras_nf.json"
)


# ============================================================
# CARREGAR E SALVAR REGRAS
# ============================================================

def carregar_regras():
    if os.path.exists(ARQUIVO):
        with open(ARQUIVO, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)

    return []


def salvar_regras():
    with open(ARQUIVO, "w", encoding="utf-8") as arquivo:
        json.dump(
            regras,
            arquivo,
            ensure_ascii=False,
            indent=4
        )


# ============================================================
# CADASTRAR REGRA
# ============================================================

def cadastrar_regra():
    print("\n========== CADASTRAR REGRA ==========")

    local = input("Local ou região: ").strip()

    tipo = input(
        "Tipo (Cidade/Região/Porto/Outro): "
    ).strip()

    print("\nEmitir NF?")
    print("1 - SIM (Código 1)")
    print("2 - NÃO (Código 53)")

    while True:
        escolha = input("Escolha: ").strip()

        if escolha == "1":
            emitir = "S"
            codigo = "1"
            break

        elif escolha == "2":
            emitir = "N"
            codigo = "53"
            break

        else:
            print("Opção inválida. Digite 1 ou 2.")

    observacao = input("Observação: ").strip()

    regra = {
        "local": local,
        "tipo": tipo,
        "codigo": codigo,
        "emitir": emitir,
        "observacao": observacao
    }

    regras.append(regra)

    salvar_regras()

    print("\nRegra cadastrada com sucesso!")

    mostrar_regra(regra)


# ============================================================
# CONSULTAR REGRA
# ============================================================

def consultar_regra(pesquisa):
    pesquisa = pesquisa.strip().lower()

    encontrados = []

    for regra in regras:
        if pesquisa in regra["local"].lower():
            encontrados.append(regra)

    return encontrados


# ============================================================
# MOSTRAR REGRA
# ============================================================

def mostrar_regra(regra):
    print("\n--------------------------------")
    print("Local:", regra["local"])
    print("Tipo:", regra["tipo"])
    print("Código NF:", regra["codigo"])

    if regra["emitir"] == "S":
        print("Emitir NF: SIM")
    else:
        print("Emitir NF: NÃO")

    print("Observação:", regra["observacao"])
    print("--------------------------------")


# ============================================================
# VER TABELA
# ============================================================

def ver_tabela():
    print("\n================ TABELA DE REGRAS ================")

    if len(regras) == 0:
        print("Nenhuma regra cadastrada.")
        return

    print(
        f"{'Nº':<4}"
        f"{'LOCAL/REGIÃO':<30}"
        f"{'TIPO':<12}"
        f"{'CÓDIGO':<10}"
        f"{'NF':<8}"
    )

    print("-" * 64)

    for numero, regra in enumerate(regras, start=1):

        if regra["emitir"] == "S":
            nf = "SIM"
        else:
            nf = "NÃO"

        print(
            f"{numero:<4}"
            f"{regra['local'][:28]:<30}"
            f"{regra['tipo'][:10]:<12}"
            f"{regra['codigo']:<10}"
            f"{nf:<8}"
        )

    print("-" * 64)


# ============================================================
# ALTERAR REGRA
# ============================================================

def alterar_regra():
    print("\n========== ALTERAR REGRA ==========")

    if len(regras) == 0:
        print("Nenhuma regra cadastrada.")
        return

    ver_tabela()

    try:
        numero = int(
            input("Digite o Nº da regra: ")
        )

    except ValueError:
        print("Digite um número válido.")
        return

    indice = numero - 1

    if indice < 0 or indice >= len(regras):
        print("Número de regra inválido.")
        return

    regra = regras[indice]

    print("\nPressione ENTER para manter o valor atual.")

    local = input(
        f"Local [{regra['local']}]: "
    ).strip()

    tipo = input(
        f"Tipo [{regra['tipo']}]: "
    ).strip()

    print(
        f"\nDecisão atual: "
        f"{'EMITIR NF' if regra['emitir'] == 'S' else 'NÃO EMITIR NF'}"
    )

    print("1 - Emitir NF (Código 1)")
    print("2 - Não emitir NF (Código 53)")
    print("ENTER - Manter atual")

    escolha = input("Escolha: ").strip()

    observacao = input(
        f"Observação [{regra['observacao']}]: "
    ).strip()

    if local:
        regra["local"] = local

    if tipo:
        regra["tipo"] = tipo

    if escolha == "1":
        regra["emitir"] = "S"
        regra["codigo"] = "1"

    elif escolha == "2":
        regra["emitir"] = "N"
        regra["codigo"] = "53"

    if observacao:
        regra["observacao"] = observacao

    salvar_regras()

    print("\nRegra alterada com sucesso!")


# ============================================================
# EXCLUIR REGRA
# ============================================================

def excluir_regra():
    print("\n========== EXCLUIR REGRA ==========")

    if len(regras) == 0:
        print("Nenhuma regra cadastrada.")
        return

    ver_tabela()

    try:
        numero = int(
            input("Digite o Nº da regra: ")
        )

    except ValueError:
        print("Digite um número válido.")
        return

    indice = numero - 1

    if indice < 0 or indice >= len(regras):
        print("Número de regra inválido.")
        return

    regra = regras[indice]

    print("\nVocê selecionou:")

    mostrar_regra(regra)

    confirmacao = input(
        "\nTem certeza que deseja excluir? (S/N): "
    ).strip().upper()

    if confirmacao == "S":
        regras.pop(indice)

        salvar_regras()

        print("Regra excluída.")

    else:
        print("Exclusão cancelada.")


# ============================================================
# MENU
# ============================================================

def menu():
    while True:

        print("\n")
        print("========================================")
        print("            CONTROLE DE NF")
        print("========================================")
        print("1 - Cadastrar regra")
        print("2 - Consultar regra")
        print("3 - Ver tabela")
        print("4 - Alterar regra")
        print("5 - Excluir regra")
        print("0 - Sair")
        print("========================================")

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":

            cadastrar_regra()

        elif opcao == "2":

            pesquisa = input(
                "Digite o local ou região: "
            ).strip()

            encontrados = consultar_regra(
                pesquisa
            )

            if len(encontrados) == 0:

                print("\nNenhuma regra encontrada.")

            else:

                for regra in encontrados:

                    mostrar_regra(regra)

        elif opcao == "3":

            ver_tabela()

        elif opcao == "4":

            alterar_regra()

        elif opcao == "5":

            excluir_regra()

        elif opcao == "0":

            print("\nPrograma encerrado.")

            break

        else:

            print("\nOpção inválida.")


# ============================================================
# CARREGAR REGRAS
# ============================================================

regras = carregar_regras()


# ============================================================
# EXECUTAR MENU SOMENTE QUANDO FOR RODADO DIRETAMENTE
# ============================================================

if __name__ == "__main__":
    menu()
