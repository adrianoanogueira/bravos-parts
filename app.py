import streamlit as st
import json
import os

# Funções auxiliares
def carregar_dados(arquivo, vazio=None):
    if not os.path.exists(arquivo) or os.stat(arquivo).st_size == 0:
        with open(arquivo, 'w') as f:
            json.dump(vazio or {}, f)
        return vazio or {}
    with open(arquivo, 'r') as f:
        return json.load(f)

def salvar_dados(arquivo, dados):
    with open(arquivo, 'w') as f:
        json.dump(dados, f, indent=4)

# Caminhos dos arquivos
ARQUIVO_CATEGORIAS = 'categorias.json'
ARQUIVO_VALORES = 'valores.json'

# Inicialização dos dados
categorias = carregar_dados(ARQUIVO_CATEGORIAS, [])
valores = carregar_dados(ARQUIVO_VALORES, {})

# Título
st.title("Gerenciador de Valores por Categoria de Serviço")

# Menu lateral
tela = st.sidebar.radio("Navegar para:", ["Adicionar Categoria", "Gerenciar Valores"])

# Função: Adicionar Categoria
def adicionar_categoria():
    st.header("Adicionar Nova Categoria")
    nova_categoria = st.text_input("Nome da nova categoria:")
    if st.button("Adicionar"):
        if nova_categoria and nova_categoria not in categorias:
            categorias.append(nova_categoria)
            salvar_dados(ARQUIVO_CATEGORIAS, categorias)
            st.success(f"Categoria '{nova_categoria}' adicionada!")
            st.experimental_rerun()
        else:
            st.warning("Categoria já existe ou está em branco.")

    st.subheader("Categorias Existentes")
    for categoria in categorias:
        col1, col2 = st.columns([4, 1])
        col1.write(f"🔹 {categoria}")
        if col2.button("Excluir", key=f"del_{categoria}"):
            categorias.remove(categoria)
            # Remover valores associados à categoria
            valores.pop(categoria, None)
            salvar_dados(ARQUIVO_CATEGORIAS, categorias)
            salvar_dados(ARQUIVO_VALORES, valores)
            st.success(f"Categoria '{categoria}' excluída com sucesso.")
            st.experimental_rerun()

# Função: Gerenciar Valores
def gerenciar_valores():
    st.header("Gerenciar Valores por Categoria")

    if not categorias:
        st.warning("Nenhuma categoria cadastrada ainda.")
        return

    for categoria in categorias:
        st.subheader(f"Categoria: {categoria}")
        itens = valores.get(categoria, [])

        novos_itens = []
        for idx, item in enumerate(itens):
            col1, col2, col3 = st.columns([3, 2, 1])
            nome = col1.text_input("Nome", value=item['nome'], key=f"{categoria}_nome_{idx}")
            valor = col2.text_input("Valor", value=item['valor'], key=f"{categoria}_valor_{idx}")
            remover = col3.checkbox("Remover", key=f"{categoria}_remove_{idx}")
            if not remover:
                novos_itens.append({'nome': nome, 'valor': valor})

        # Adicionar novo item
        st.markdown("---")
        col1, col2 = st.columns(2)
        novo_nome = col1.text_input(f"Novo item - Nome ({categoria})", key=f"{categoria}_novo_nome")
        novo_valor = col2.text_input(f"Novo item - Valor ({categoria})", key=f"{categoria}_novo_valor")
        if st.button(f"Adicionar Item em {categoria}", key=f"add_item_{categoria}"):
            if novo_nome and novo_valor:
                novos_itens.append({'nome': novo_nome, 'valor': novo_valor})
                st.success(f"Item '{novo_nome}' adicionado!")
            else:
                st.warning("Preencha nome e valor para adicionar.")

        # Atualiza os valores
        valores[categoria] = novos_itens

    if st.button("Salvar Todas as Alterações"):
        salvar_dados(ARQUIVO_VALORES, valores)
        st.success("Valores salvos com sucesso!")

# Executa a tela correspondente
if tela == "Adicionar Categoria":
    adicionar_categoria()
else:
    gerenciar_valores()
