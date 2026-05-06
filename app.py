import streamlit as st
import requests

# ===== SESSION STATE =====
if "resultados_busca" not in st.session_state:
	st.session_state.resultados_busca = None

if "data" not in st.session_state:
	st.session_state.data = None

if "selecionado" not in st.session_state:
	st.session_state.selecionado = None

if "historico" not in st.session_state:
	st.session_state.historico = []
      
if "apagados" not in st.session_state:
	st.session_state.apagados = []

if "limpou_tudo" not in st.session_state:
	st.session_state.limpou_tudo = False

st.title("CiteFix - Gerador de Referências")

# ===== CRIAÇÃO DAS ABAS =====
tab_artigos, tab_livros, tab_manual, tab_historico = st.tabs([
    "📄 Artigos (DOI/Título)", 
    "📚 Livros", 
    "✍️ Manual", 
    "🕰️ Histórico"
])

# ===== FORM =====
with tab_artigos:
    with st.form("form_busca"):
        entrada = st.text_input("Digite o DOI OU o título do artigo:")
        submit = st.form_submit_button("Buscar")

    # ===== BUSCA =====
    if submit:
        st.session_state.resultados_busca = None
        st.session_state.data = None
        st.session_state.selecionado = None
        st.session_state.apagados = []
        st.session_state.limpou_tudo = False

        if entrada:

            # DOI
            if "/" in entrada:
                url = f"https://api.crossref.org/works/{entrada}"
                response = requests.get(url)

                if response.status_code == 200:
                    st.session_state.data = response.json()["message"]
                else:
                    st.error("Erro ao buscar DOI.")

            # TÍTULO
            else:
                url = f"https://api.crossref.org/works?query.title={entrada}&rows=5"
                response = requests.get(url)

                if response.status_code == 200:
                    resultados = response.json()["message"]["items"]

                    if not resultados:
                        st.error("Nenhum resultado encontrado.")
                    else:
                        st.session_state.resultados_busca = resultados
                else:
                    st.error("Erro ao buscar título.")

    def formatar_primeiro_autor(autor):
        family = autor.get("family", "")
        given = autor.get("given", "")

        if not family:
            return "Autor desconhecido"

        family = family.upper()

        if given and given.split():
            inicial = given.split()[0][0].upper()
            return f"{family}, {inicial}."
        
        return family

    # ===== FUNÇÃO DE GERAR REFERÊNCIA =====
    def gerar_referencia(data):
        # 1. Tratamento do Título, Pontuação e Tags HTML
        titulo = data.get("title", ["Sem título"])[0].strip()
        
        # Filtro avançado para capturar as diferentes formas que o Crossref manda o itálico
        titulo = titulo.replace("<i>", "*").replace("</i>", "*")
        titulo = titulo.replace("<I>", "*").replace("</I>", "*")
        titulo = titulo.replace("<italic>", "*").replace("</italic>", "*")
        titulo = titulo.replace("<ITALIC>", "*").replace("</ITALIC>", "*")
        titulo = titulo.replace("<em>", "*").replace("</em>", "*")
        titulo = titulo.replace("&lt;i&gt;", "*").replace("&lt;/i&gt;", "*")
        
        # Se o título já terminar em pontuação, não adiciona o ponto final extra
        if titulo and titulo[-1] in ["?", "!", "."]:
            titulo_com_pontuacao = titulo
        else:
            titulo_com_pontuacao = f"{titulo}."

        # 2. Tratamento da Data (Ano vazio = [s.d.] - Sem Data)
        data_parts = data.get("issued", {}).get("date-parts", [[None]])
        ano = data_parts[0][0] if len(data_parts[0]) > 0 and data_parts[0][0] is not None else "[s.d.]"
        mes = data_parts[0][1] if len(data_parts[0]) > 1 else ""
        dia = data_parts[0][2] if len(data_parts[0]) > 2 else ""
        
        journal = data.get("container-title", [""])[0]
        meses = ["jan.", "fev.", "mar.", "abr.", "maio", "jun.", "jul.", "ago.", "set.", "out.", "nov.", "dez."]
        mes_formatado = meses[mes-1] if mes and isinstance(mes, int) and mes <= 12 else ""

        volume = data.get("volume", "")
        numero = data.get("issue", "")
        
        # 3. Tratamento de Páginas vs Article Number
        paginas = data.get("page", "")
        article_number = data.get("article-number", "") 

        journal_formatado = f"*{journal}*" if journal else ""

        # 4. Tratamento de Autores (Se não houver autor)
        autores = data.get("author", [])
        autores_formatados = []
        
        for autor in autores:
            sobrenome = autor.get("family", "")
            nome = autor.get("given", "")
            if sobrenome: # Garante que só processa se o sobrenome existir
                iniciais = " ".join([n[0].upper() + "." for n in nome.split() if n])
                autores_formatados.append(f"{sobrenome.upper()}, {iniciais}")

        if len(autores_formatados) >= 4:
            autores_str = autores_formatados[0] + " et al."
        elif len(autores_formatados) > 0:
            autores_str = "; ".join(autores_formatados).rstrip(".")
        else:
            autores_str = "" # Sem autor

        # 5. Montagem da Referência
        if autores_str:
            if autores_str.endswith("et al."):
                referencia = f"{autores_str} {titulo_com_pontuacao}"
            else:
                referencia = f"{autores_str}. {titulo_com_pontuacao}"
        else:
            # Se não tem autor, a ABNT começa pelo título
            referencia = f"{titulo_com_pontuacao}"

        if journal_formatado:
            referencia += f" {journal_formatado}"

        if volume:
            referencia += f", v. {volume}"

        if numero:
            referencia += f", n. {numero}"

        # Adiciona a página ou o article number
        if paginas:
            paginas = paginas.strip()
            if "-" in paginas:
                referencia += f", p. {paginas}"
            else:
                referencia += f", p. {paginas}" # Tem revista que tem só uma página
        elif article_number:
            referencia += f", {article_number}" # Substitui a falta de página pelo Artigo

        # Monta o final com a data
        if dia and mes_formatado:
            referencia += f", {dia} {mes_formatado} {ano}"
        elif mes_formatado:
            referencia += f", {mes_formatado} {ano}"
        else:
            referencia += f", {ano}"

        return referencia.rstrip(".") + "."

    def gerar_citacao(autores, ano):
        # Se ano for None, define como [s.d.]
        ano_str = ano if ano else "[s.d.]"

        if not autores:
            return f"(Autor desconhecido, {ano_str})"

        nomes = []

        for a in autores:
            sobrenome = a.get("family", "")
            if sobrenome:
                nomes.append(sobrenome.title())

        if len(nomes) == 0:
            return f"(Autor desconhecido, {ano_str})"

        elif len(nomes) <= 3:
            return f"({'; '.join(nomes)}, {ano_str})"

        else:
            return f"({nomes[0]} et al., {ano_str})"

    # ===== RESULTADO DOI =====
    if st.session_state.data and not st.session_state.resultados_busca:

        data = st.session_state.data

        # Pega o título e já aplica a limpeza de tags
        titulo_item = data.get("title", ["Sem título"])[0].strip()
        titulo_item = titulo_item.replace("<i>", "*").replace("</i>", "*")
        titulo_item = titulo_item.replace("<I>", "*").replace("</I>", "*")
        titulo_item = titulo_item.replace("<italic>", "*").replace("</italic>", "*")
        titulo_item = titulo_item.replace("<ITALIC>", "*").replace("</ITALIC>", "*")
        titulo_item = titulo_item.replace("<em>", "*").replace("</em>", "*")
        titulo_item = titulo_item.replace("&lt;i&gt;", "*").replace("&lt;/i&gt;", "*")

        autores = data.get("author", [])

        autores = data.get("author", [])
        if autores:
            primeiro = autores[0]
            nome = formatar_primeiro_autor(primeiro)
            autores_str = f"{nome} et al."
        else:
            autores_str = "Autor desconhecido"

        data_parts = data.get("issued", {}).get("date-parts", [[None]])
        ano = data_parts[0][0] if len(data_parts[0]) > 0 else None

        st.write("### Resultado:")

        st.markdown(f"**{titulo_item}**")

        autores = data.get("author", [])
        data_parts = data.get("issued", {}).get("date-parts", [[None]])
        ano = data_parts[0][0] if len(data_parts[0]) > 0 else None

        citacao = gerar_citacao(autores, ano)

        ref = gerar_referencia(data)

        st.markdown(f"**Citação no texto:** {citacao}")

        st.success(f"Referência:\n\n{ref}")

        # ===== histórico =====
        if not st.session_state.limpou_tudo and ref not in st.session_state.apagados:
            if ref not in st.session_state.historico:
                st.session_state.historico.append(ref)

    # ===== LISTA DE TÍTULOS =====
    if st.session_state.resultados_busca:

        st.write("### Selecione o artigo correto:")

        for item in st.session_state.resultados_busca:
            titulo_item = item.get("title", ["Sem título"])[0].strip()
            
            # Limpa as tags do título que aparece na lista
            titulo_item = titulo_item.replace("<i>", "*").replace("</i>", "*")
            titulo_item = titulo_item.replace("<I>", "*").replace("</I>", "*")
            titulo_item = titulo_item.replace("<italic>", "*").replace("</italic>", "*")
            titulo_item = titulo_item.replace("<ITALIC>", "*").replace("</ITALIC>", "*")
            titulo_item = titulo_item.replace("<em>", "*").replace("</em>", "*")
            titulo_item = titulo_item.replace("&lt;i&gt;", "*").replace("&lt;/i&gt;", "*")

            # autores
            autores = item.get("author", [])
            if autores:
                primeiro = autores[0]
                nome = formatar_primeiro_autor(primeiro)
                autores_str = f"{nome} et al."
            else:
                autores_str = "Autor desconhecido"

            # ano
            data_parts = item.get("issued", {}).get("date-parts", [[None]])
            ano = data_parts[0][0]

            col1, col2 = st.columns([8, 2])

            with col1:
                citacao_preview = gerar_citacao(autores, ano)

                st.markdown(f"**{titulo_item}**")
                st.markdown(f"Citação no texto: {citacao_preview}")

            with col2:
                key_id = item.get("DOI", titulo_item)

                if st.button("Selecionar", key=key_id):
                    st.session_state.selecionado = key_id
                    st.session_state.apagados = []
                    st.session_state.limpou_tudo = False

            # 👇 FORA DA COLUNA → largura normal
            if st.session_state.selecionado == key_id:
                ref = gerar_referencia(item)

                # ===== pega dados para citação =====
                autores = item.get("author", [])
                data_parts = item.get("issued", {}).get("date-parts", [[None]])
                ano = data_parts[0][0]

                citacao = gerar_citacao(autores, ano)

                # ===== exibição =====
                st.success(f"Referência:\n\n{ref}")

                # ===== histórico =====
                if not st.session_state.limpou_tudo and ref not in st.session_state.apagados:
                    if ref not in st.session_state.historico:
                        st.session_state.historico.append(ref)

            st.markdown("---")

# ===== ABA 2: LIVROS =====
with tab_livros:
    st.info("Em breve: Busca automática de livros por título, autor ou ISBN.")

# ===== ABA 3: MANUAL =====
with tab_manual:
    st.info("Em breve: Formulário para gerar referências de TCCs, Teses, Capítulos de Livro, etc.")

# ===== MENSAGEM FINAL =====
if submit and not entrada:
	st.write("Digite um DOI ou título.")

# ===== HISTÓRICO DE REFERÊNCIAS =====
with tab_historico:
    st.write("## 📚 Seu Histórico")

    # Só mostra o histórico se ele não estiver vazio
    if st.session_state.historico:
        
        # Cria duas colunas para alinhar o botão "Limpar Tudo" à direita
        col_vazia, col_limpar = st.columns([8, 2])
        with col_limpar:
            if st.button("🗑️ Limpar Tudo", use_container_width=True):
                st.session_state.historico = []
                st.session_state.limpou_tudo = True
                st.rerun()

        st.markdown("---")

        # Ordena o histórico alfabeticamente
        historico_ordenado = sorted(st.session_state.historico, key=str.lower)

        # O enumerate(historico_ordenado) serve para criar um ID único (i) para cada botão
        for i, ref in enumerate(historico_ordenado):
            col_texto, col_botao_del = st.columns([9, 1])

            with col_texto:
                st.markdown(ref)

            with col_botao_del:
                if st.button("❌", key=f"del_{i}"):
                    st.session_state.historico.remove(ref)
                    st.session_state.apagados.append(ref)
                    st.rerun()
            
            st.write("") # Espaço entre as referências
    else:
        st.info("Seu histórico está vazio. Faça uma busca para adicionar referências!")