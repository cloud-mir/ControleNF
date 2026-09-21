import json
import os
import psycopg


# ============================================================
# CONFIGURAÇÃO
# ============================================================

PASTA_CONTROLE_NF = os.path.dirname(
    os.path.abspath(__file__)
)

ARQUIVO = os.path.join(
    PASTA_CONTROLE_NF,
    "regras_nf.json"
)

DATABASE_URL = os.environ.get(
    "DATABASE_URL"
)


# ============================================================
# CONEXÃO COM O BANCO
# ============================================================

def conectar_banco():

    if not DATABASE_URL:

        raise RuntimeError(
            "DATABASE_URL não foi configurada."
        )

    return psycopg.connect(
        DATABASE_URL
    )


# ============================================================
# CRIAR TABELA
# ============================================================

def criar_tabela():

    with conectar_banco() as conn:

        with conn.cursor() as cursor:

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS regras_nf (
                    id BIGSERIAL PRIMARY KEY,
                    local TEXT NOT NULL,
                    tipo TEXT,
                    codigo TEXT,
                    emitir TEXT,
                    observacao TEXT
                )
            """)


# ============================================================
# MIGRAR REGRAS DO JSON PARA O BANCO
# ============================================================

def migrar_json():

    if not os.path.exists(ARQUIVO):

        return

    try:

        with open(
            ARQUIVO,
            "r",
            encoding="utf-8"
        ) as arquivo:

            dados = json.load(
                arquivo
            )

    except (
        json.JSONDecodeError,
        OSError
    ):

        return

    if not isinstance(
        dados,
        list
    ):

        return

    with conectar_banco() as conn:

        with conn.cursor() as cursor:

            cursor.execute("""
                SELECT COUNT(*)
                FROM regras_nf
            """)

            quantidade = cursor.fetchone()[0]

            # Se o banco já possui regras,
            # não importa o JSON novamente.
            if quantidade > 0:

                return

            for regra in dados:

                if not isinstance(
                    regra,
                    dict
                ):

                    continue

                local = str(
                    regra.get(
                        "local",
                        ""
                    )
                ).strip()

                if not local:

                    continue

                tipo = str(
                    regra.get(
                        "tipo",
                        ""
                    )
                ).strip()

                codigo = str(
                    regra.get(
                        "codigo",
                        ""
                    )
                ).strip()

                emitir = str(
                    regra.get(
                        "emitir",
                        ""
                    )
                ).strip().upper()

                observacao = str(
                    regra.get(
                        "observacao",
                        ""
                    )
                ).strip()

                cursor.execute("""
                    INSERT INTO regras_nf (
                        local,
                        tipo,
                        codigo,
                        emitir,
                        observacao
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                """, (
                    local,
                    tipo,
                    codigo,
                    emitir,
                    observacao
                ))


# ============================================================
# INICIALIZAR CONTROLE NF
# ============================================================

def inicializar_regras():

    criar_tabela()

    migrar_json()

    carregar_regras()


# ============================================================
# CARREGAR REGRAS
# ============================================================

def carregar_regras():

    global regras

    try:

        with conectar_banco() as conn:

            with conn.cursor() as cursor:

                cursor.execute("""
                    SELECT
                        id,
                        local,
                        tipo,
                        codigo,
                        emitir,
                        observacao
                    FROM regras_nf
                    ORDER BY id
                """)

                resultados = cursor.fetchall()

    except Exception as erro:

        print(
            "Erro ao carregar regras:",
            erro
        )

        regras = []

        return regras

    regras = []

    for resultado in resultados:

        regras.append({

            "id": resultado[0],

            "local": resultado[1],

            "tipo": resultado[2],

            "codigo": resultado[3],

            "emitir": resultado[4],

            "observacao": resultado[5]

        })

    return regras


# ============================================================
# SALVAR REGRAS
# ============================================================

def salvar_regras():

    with conectar_banco() as conn:

        with conn.cursor() as cursor:

            for regra in regras:

                regra_id = regra.get(
                    "id"
                )

                local = str(
                    regra.get(
                        "local",
                        ""
                    )
                ).strip()

                if not local:

                    continue

                tipo = str(
                    regra.get(
                        "tipo",
                        ""
                    )
                ).strip()

                codigo = str(
                    regra.get(
                        "codigo",
                        ""
                    )
                ).strip()

                emitir = str(
                    regra.get(
                        "emitir",
                        ""
                    )
                ).strip().upper()

                observacao = str(
                    regra.get(
                        "observacao",
                        ""
                    )
                ).strip()

                if regra_id is None:

                    cursor.execute("""
                        INSERT INTO regras_nf (
                            local,
                            tipo,
                            codigo,
                            emitir,
                            observacao
                        )
                        VALUES (
                            %s,
                            %s,
                            %s,
                            %s,
                            %s
                        )
                        RETURNING id
                    """, (
                        local,
                        tipo,
                        codigo,
                        emitir,
                        observacao
                    ))

                    novo_id = cursor.fetchone()[0]

                    regra["id"] = novo_id

                else:

                    cursor.execute("""
                        UPDATE regras_nf
                        SET
                            local = %s,
                            tipo = %s,
                            codigo = %s,
                            emitir = %s,
                            observacao = %s
                        WHERE id = %s
                    """, (
                        local,
                        tipo,
                        codigo,
                        emitir,
                        observacao,
                        regra_id
                    ))

            # ------------------------------------------------
            # Remover do banco regras que não existem mais
            # na lista atual
            # ------------------------------------------------

            ids = [
                regra.get("id")
                for regra in regras
                if regra.get("id") is not None
            ]

            if ids:

                cursor.execute("""
                    DELETE FROM regras_nf
                    WHERE id <> ALL(%s)
                """, (
                    ids,
                ))

            else:

                cursor.execute("""
                    DELETE FROM regras_nf
                """)


# ============================================================
# CADASTRAR REGRA
# ============================================================

def cadastrar_regra():

    print(
        "\n========== CADASTRAR REGRA =========="
    )

    local = input(
        "Local ou região: "
    ).strip()

    tipo = input(
        "Tipo (Cidade/Região/Porto/Outro): "
    ).strip()

    print(
        "\nEmitir NF?"
    )

    print(
        "1 - SIM (Código 1)"
    )

    print(
        "2 - NÃO (Código 53)"
    )

    while True:

        escolha = input(
            "Escolha: "
        ).strip()

        if escolha == "1":

            emitir = "S"
            codigo = "1"

            break

        elif escolha == "2":

            emitir = "N"
            codigo = "53"

            break

        print(
            "Opção inválida. Digite 1 ou 2."
        )

    observacao = input(
        "Observação: "
    ).strip()

    regra = {

        "local": local,

        "tipo": tipo,

        "codigo": codigo,

        "emitir": emitir,

        "observacao": observacao

    }

    regras.append(
        regra
    )

    salvar_regras()

    print(
        "\nRegra cadastrada com sucesso!"
    )

    mostrar_regra(
        regra
    )


# ============================================================
# CONSULTAR REGRA
# ============================================================

def consultar_regra(
    pesquisa
):

    pesquisa = pesquisa.strip().lower()

    if not pesquisa:

        return []

    carregar_regras()

    return [

        regra

        for regra in regras

        if pesquisa in str(
            regra.get(
                "local",
                ""
            )
        ).lower()

    ]


# ============================================================
# MOSTRAR REGRA
# ============================================================

def mostrar_regra(
    regra
):

    print(
        "\n--------------------------------"
    )

    print(
        "Local:",
        regra.get(
            "local",
            ""
        )
    )

    print(
        "Tipo:",
        regra.get(
            "tipo",
            ""
        )
    )

    print(
        "Código NF:",
        regra.get(
            "codigo",
            ""
        )
    )

    print(
        "Emitir NF: "
        + (
            "SIM"
            if regra.get(
                "emitir"
            ) == "S"
            else "NÃO"
        )
    )

    print(
        "Observação:",
        regra.get(
            "observacao",
            ""
        )
    )

    print(
        "--------------------------------"
    )


# ============================================================
# VER TABELA
# ============================================================

def ver_tabela():

    carregar_regras()

    print(
        "\n================ TABELA DE REGRAS ================"
    )

    if not regras:

        print(
            "Nenhuma regra cadastrada."
        )

        return

    print(
        f"{'Nº':<4}"
        f"{'LOCAL/REGIÃO':<30}"
        f"{'TIPO':<12}"
        f"{'CÓDIGO':<10}"
        f"{'NF':<8}"
    )

    print(
        "-" * 64
    )

    for numero, regra in enumerate(
        regras,
        start=1
    ):

        nf = (
            "SIM"
            if regra.get(
                "emitir"
            ) == "S"
            else "NÃO"
        )

        print(
            f"{numero:<4}"
            f"{str(regra.get('local',''))[:28]:<30}"
            f"{str(regra.get('tipo',''))[:10]:<12}"
            f"{str(regra.get('codigo','')):<10}"
            f"{nf:<8}"
        )

    print(
        "-" * 64
    )


# ============================================================
# ALTERAR REGRA
# ============================================================

def alterar_regra():

    carregar_regras()

    print(
        "\n========== ALTERAR REGRA =========="
    )

    if not regras:

        print(
            "Nenhuma regra cadastrada."
        )

        return

    ver_tabela()

    try:

        numero = int(
            input(
                "Digite o Nº da regra: "
            )
        )

    except ValueError:

        print(
            "Digite um número válido."
        )

        return

    indice = numero - 1

    if (
        indice < 0
        or indice >= len(regras)
    ):

        print(
            "Número de regra inválido."
        )

        return

    regra = regras[indice]

    print(
        "\nPressione ENTER para manter o valor atual."
    )

    local = input(
        f"Local [{regra.get('local','')}]: "
    ).strip()

    tipo = input(
        f"Tipo [{regra.get('tipo','')}]: "
    ).strip()

    print(
        "\nDecisão atual: "
        + (
            "EMITIR NF"
            if regra.get(
                "emitir"
            ) == "S"
            else "NÃO EMITIR NF"
        )
    )

    print(
        "1 - Emitir NF (Código 1)"
    )

    print(
        "2 - Não emitir NF (Código 53)"
    )

    print(
        "ENTER - Manter atual"
    )

    escolha = input(
        "Escolha: "
    ).strip()

    observacao = input(
        f"Observação [{regra.get('observacao','')}]: "
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

    print(
        "\nRegra alterada com sucesso!"
    )


# ============================================================
# EXCLUIR REGRA
# ============================================================

def excluir_regra():

    carregar_regras()

    print(
        "\n========== EXCLUIR REGRA =========="
    )

    if not regras:

        print(
            "Nenhuma regra cadastrada."
        )

        return

    ver_tabela()

    try:

        numero = int(
            input(
                "Digite o Nº da regra: "
            )
        )

    except ValueError:

        print(
            "Digite um número válido."
        )

        return

    indice = numero - 1

    if (
        indice < 0
        or indice >= len(regras)
    ):

        print(
            "Número de regra inválido."
        )

        return

    regra = regras[indice]

    print(
        "\nVocê selecionou:"
    )

    mostrar_regra(
        regra
    )

    confirmacao = input(
        "\nTem certeza que deseja excluir? (S/N): "
    ).strip().upper()

    if confirmacao == "S":

        regras.pop(
            indice
        )

        salvar_regras()

        print(
            "Regra excluída."
        )

    else:

        print(
            "Exclusão cancelada."
        )


# ============================================================
# MENU
# ============================================================

def menu():

    while True:

        print(
            "\n========================================"
        )

        print(
            "            CONTROLE DE NF"
        )

        print(
            "========================================"
        )

        print(
            "1 - Cadastrar regra"
        )

        print(
            "2 - Consultar regra"
        )

        print(
            "3 - Ver tabela"
        )

        print(
            "4 - Alterar regra"
        )

        print(
            "5 - Excluir regra"
        )

        print(
            "0 - Sair"
        )

        print(
            "========================================"
        )

        opcao = input(
            "Escolha uma opção: "
        ).strip()

        if opcao == "1":

            cadastrar_regra()

        elif opcao == "2":

            pesquisa = input(
                "Digite o local ou região: "
            ).strip()

            encontrados = consultar_regra(
                pesquisa
            )

            if not encontrados:

                print(
                    "\nNenhuma regra encontrada."
                )

            else:

                for regra in encontrados:

                    mostrar_regra(
                        regra
                    )

        elif opcao == "3":

            ver_tabela()

        elif opcao == "4":

            alterar_regra()

        elif opcao == "5":

            excluir_regra()

        elif opcao == "0":

            print(
                "\nPrograma encerrado."
            )

            break

        else:

            print(
                "\nOpção inválida."
            )


# ============================================================
# REGRAS
# ============================================================

regras = carregar_regras()


# ============================================================
# EXECUTAR LOCALMENTE
# ============================================================

if __name__ == "__main__":

    if DATABASE_URL:

        try:

            inicializar_regras()

        except Exception as erro:

            print(
                "ERRO AO INICIALIZAR REGRAS:"
            )

            print(
                erro
            )

    menu()
