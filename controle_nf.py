import json
import os

PASTA_CONTROLE_NF = os.path.dirname(os.path.abspath(__file__))
ARQUIVO = os.path.join(PASTA_CONTROLE_NF, "regras_nf.json")

def carregar_regras():
    if os.path.exists(ARQUIVO):
        try:
            with open(ARQUIVO, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)
            if isinstance(dados, list):
                return dados
        except (json.JSONDecodeError, OSError):
            pass
    return []

def salvar_regras():
    with open(ARQUIVO, "w", encoding="utf-8") as arquivo:
        json.dump(regras, arquivo, ensure_ascii=False, indent=4)

def cadastrar_regra():
    print("\n========== CADASTRAR REGRA ==========")
    local = input("Local ou região: ").strip()
    tipo = input("Tipo (Cidade/Região/Porto/Outro): ").strip()
    print("\nEmitir NF?")
    print("1 - SIM (Código 1)")
    print("2 - NÃO (Código 53)")
    while True:
        escolha = input("Escolha: ").strip()
        if escolha == "1":
            emitir, codigo = "S", "1"
            break
        elif escolha == "2":
            emitir, codigo = "N", "53"
            break
        print("Opção inválida. Digite 1 ou 2.")
    observacao = input("Observação: ").strip()
    regra = {"local": local, "tipo": tipo, "codigo": codigo, "emitir": emitir, "observacao": observacao}
    regras.append(regra)
    salvar_regras()
    print("\nRegra cadastrada com sucesso!")
    mostrar_regra(regra)

def consultar_regra(pesquisa):
    pesquisa = pesquisa.strip().lower()
    if not pesquisa:
        return []
    return [r for r in regras if pesquisa in str(r.get("local", "")).lower()]

def mostrar_regra(regra):
    print("\n--------------------------------")
    print("Local:", regra.get("local", ""))
    print("Tipo:", regra.get("tipo", ""))
    print("Código NF:", regra.get("codigo", ""))
    print("Emitir NF: " + ("SIM" if regra.get("emitir") == "S" else "NÃO"))
    print("Observação:", regra.get("observacao", ""))
    print("--------------------------------")

def ver_tabela():
    print("\n================ TABELA DE REGRAS ================")
    if not regras:
        print("Nenhuma regra cadastrada.")
        return
    print(f"{'Nº':<4}{'LOCAL/REGIÃO':<30}{'TIPO':<12}{'CÓDIGO':<10}{'NF':<8}")
    print("-" * 64)
    for numero, regra in enumerate(regras, start=1):
        nf = "SIM" if regra.get("emitir") == "S" else "NÃO"
        print(f"{numero:<4}{str(regra.get('local',''))[:28]:<30}{str(regra.get('tipo',''))[:10]:<12}{str(regra.get('codigo','')):<10}{nf:<8}")
    print("-" * 64)

def alterar_regra():
    print("\n========== ALTERAR REGRA ==========")
    if not regras:
        print("Nenhuma regra cadastrada.")
        return
    ver_tabela()
    try:
        numero = int(input("Digite o Nº da regra: "))
    except ValueError:
        print("Digite um número válido.")
        return
    indice = numero - 1
    if indice < 0 or indice >= len(regras):
        print("Número de regra inválido.")
        return
    regra = regras[indice]
    print("\nPressione ENTER para manter o valor atual.")
    local = input(f"Local [{regra.get('local','')}]: ").strip()
    tipo = input(f"Tipo [{regra.get('tipo','')}]: ").strip()
    print("\nDecisão atual: " + ("EMITIR NF" if regra.get("emitir") == "S" else "NÃO EMITIR NF"))
    print("1 - Emitir NF (Código 1)")
    print("2 - Não emitir NF (Código 53)")
    print("ENTER - Manter atual")
    escolha = input("Escolha: ").strip()
    observacao = input(f"Observação [{regra.get('observacao','')}]: ").strip()
    if local:
        regra["local"] = local
    if tipo:
        regra["tipo"] = tipo
    if escolha == "1":
        regra["emitir"], regra["codigo"] = "S", "1"
    elif escolha == "2":
        regra["emitir"], regra["codigo"] = "N", "53"
    if observacao:
        regra["observacao"] = observacao
    salvar_regras()
    print("\nRegra alterada com sucesso!")

def excluir_regra():
    print("\n========== EXCLUIR REGRA ==========")
    if not regras:
        print("Nenhuma regra cadastrada.")
        return
    ver_tabela()
    try:
        numero = int(input("Digite o Nº da regra: "))
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
    confirmacao = input("\nTem certeza que deseja excluir? (S/N): ").strip().upper()
    if confirmacao == "S":
        regras.pop(indice)
        salvar_regras()
        print("Regra excluída.")
    else:
        print("Exclusão cancelada.")

def menu():
    while True:
        print("\n========================================")
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
            pesquisa = input("Digite o local ou região: ").strip()
            encontrados = consultar_regra(pesquisa)
            if not encontrados:
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

regras = carregar_regras()

if __name__ == "__main__":
    menu()
