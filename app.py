import streamlit as st
import json
import os
from hashlib import sha256

# Configurações iniciais
ARQUIVO_VALORES = "valores.json"
ARQUIVO_CATEGORIAS = "categorias.json"

# Categorias padrão
CATEGORIAS_PADRAO = [
    ("FREIO", 6), ("TRANSMISSAO", 7), ("ALINHAMENTO/BALANCEAMENTO", 9),
    ("MOTOR", 10), ("SUSPENSAO", 11), ("LIMPEZA VALV INJETORAS", 12),
    ("RETIFICA DISCO/TAMBOR", 13), ("DIRECAO", 14), ("SERVICO TERCEIRIZADO", 15),
    ("OUTROS - GERAL", 17), ("CAMBAGEM/CASTER/EIXO TRAS", 18), ("OUTROS - ESPECIFICO", 19),
    ("GNV", 21), ("TOWNER", 23), ("PERFORMANCE", 24), ("AR CONDICIONADO", 25),
    ("VENDA DIRETA - GNV", 26), ("TORNO", 27)
]

# Senhas criptografadas (SHA-256)
USUARIOS = {"ADRIANO": "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"}  # Hash de "123"

# Funções utilitárias
def carregar_json(arquivo):
    """Carrega um arquivo JSON. Retorna um dicionário vazio se o arquivo não existir."""
    if os.path.exists(arquivo):
        with open(arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_json(arquivo, dados):
    """Salva um dicionário em um arquivo JSON."""
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4)

def hash_senha(senha):
    """Gera o hash SHA-256 de uma senha."""
    return sha256(senha.encode()).hexdigest()

# Tela principal
def tela_principal():
    st.title("Atualização de Valores por Categoria de Serviço")

    valores_salvos = carregar_json(ARQUIVO_VALORES)
    categorias_extra = carregar_json(ARQUIVO_CATEGORIAS)

    # Combina categorias padrão e adicionais
    categorias = CATEGORIAS_PADRAO + [(nome, int(codigo)) for codigo, nome in categorias_extra.items()]
    categorias.sort(key=lambda x: x[1])

    # Editar valores de venda
    st.subheader("Editar Valores de Venda")
    valores_atualizados = {}
    for nome, codigo in categorias:
        valor = valores_salvos.get(str(codigo), "")
        novo_valor = st.text_input(
            f"{nome} (CÓDIGO {codigo})",
            value=valor,
            key=f"val_{codigo}"
        )
        valores_atualizados[str(codigo)] = novo_valor

    # Salvar automaticamente
    salvar_json(ARQUIVO_VALORES, valores_atualizados)
    st.success("Alterações salvas automaticamente.")

    # Gerar script SQL
    st.divider()
    st.subheader("Gerar Script SQL")
    if st.button("Gerar SQL"):
        comandos_sql = []
        for codigo, valor in valores_atualizados.items():
            if valor.strip():
                try:
                    valor_float = float(valor)
                    comandos_sql.append(
                        f"UPDATE OFI_SERVICO SET VAL_SERVICO_UNITARIO = {valor_float} WHERE CATEGORIA_SERVICO = {codigo};"
                    )
                except ValueError:
                    st.error(f"Valor inválido para código {codigo}: {valor}")
                    return

        if comandos_sql:
            sql_content = "\n".join(comandos_sql)
            st.code(sql_content, language="sql")

            # Botão para download do arquivo .sql
            st.download_button(
                label="Baixar Arquivo SQL",
                data=sql_content,
                file_name="script.sql",
                mime="application/sql"
            )
        else:
            st.warning("Nenhum valor preenchido.")

    # Gerenciar categorias adicionais
    st.divider()
    st.subheader("Gerenciar Categorias Adicionais")
    with st.form("nova_categoria"):
        nome_novo = st.text_input("Nome da nova categoria")
        codigo_novo = st.number_input("Código da nova categoria", step=1, format="%d")
        enviar = st.form_submit_button("Adicionar")
        if enviar:
            if str(int(codigo_novo)) in categorias_extra:
                st.error("Código já existente!")
            elif not nome_novo.strip():
                st.error("O nome da categoria não pode estar vazio.")
            else:
                categorias_extra[str(int(codigo_novo))] = nome_novo
                salvar_json(ARQUIVO_CATEGORIAS, categorias_extra)
                st.success("Categoria adicionada!")

    # Excluir categoria adicional
    st.divider()
    st.subheader("Excluir Categoria Adicional")
    codigos_adicionais = list(categorias_extra.keys())
    if not codigos_adicionais:
        st.info("Nenhuma categoria adicional cadastrada.")
    else:
        codigo_excluir = st.selectbox("Selecione a categoria para excluir", codigos_adicionais)
        if st.button("Confirmar Exclusão"):
            nome_excluido = categorias_extra.pop(codigo_excluir)
            valores_salvos.pop(codigo_excluir, None)
            salvar_json(ARQUIVO_CATEGORIAS, categorias_extra)
            salvar_json(ARQUIVO_VALORES, valores_salvos)
            st.success(f"Categoria '{nome_excluido}' excluída!")

# Tela de login
def tela_login():
    st.title("Login")

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if usuario in USUARIOS and USUARIOS[usuario] == hash_senha(senha):
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos.")

# Controle de acesso
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if st.session_state["autenticado"]:
    tela_principal()
else:
    tela_login()