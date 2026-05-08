import streamlit as st
import requests
import re

# ===== CONFIGURAÇÃO DA PÁGINA =====
st.set_page_config(
    page_title="CiteFix | Gerador ABNT",
    page_icon="🪶",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ===== CSS AVANÇADO (DESIGN PREMIUM) =====
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}

        .stApp {
            background-color: #F8FAFC !important;
            font-family: 'Inter', sans-serif;
            color: #334155;
        }

        .block-container {
            padding-top: 3rem;
            padding-bottom: 4rem;
            max-width: 800px;
        }

        h1, h2, h3, h4 {
            color: #0F172A;
            font-weight: 700 !important;
            letter-spacing: -0.02em;
        }

        /* ===== TABS ===== */
        .stTabs [data-baseweb="tab-list"] {
            gap: 20px;
            border-bottom: 2px solid #E2E8F0;
            margin-bottom: 1.5rem;
        }
        .stTabs [data-baseweb="tab"] {
            padding-top: 15px;
            padding-bottom: 15px;
            color: #64748B;
            font-weight: 600;
            border: none;
            background-color: transparent;
        }
        .stTabs [aria-selected="true"] {
            color: #0F766E !important; 
            border-bottom: 3px solid #0F766E !important;
        }

        /* ===== BARRA DE PESQUISA ELEGANTE E FORMULÁRIOS ===== */
        .stTextInput>div>div>input {
            background-color: #FFFFFF !important;
            color: #1E293B !important;
            border-radius: 8px !important;
            border: 1px solid #CBD5E1 !important;
            padding: 14px 16px !important; 
            font-size: 1rem !important;
            line-height: 1.5 !important;
            caret-color: #0F766E !important; 
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
            transition: all 0.2s ease !important;
        }
        
        input[aria-label="Busca"] {
            padding-right: 45px !important; 
            background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="%2394A3B8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>');
            background-repeat: no-repeat !important;
            background-position: right 14px center !important;
        }
        
        .stTextInput>div>div>input:focus {
            border-color: #0F766E !important;
            box-shadow: 0 0 0 2px rgba(15, 118, 110, 0.2) !important;
        }
        
        .stTextInput>div>div>input::placeholder {
            color: #94A3B8 !important; 
            opacity: 1 !important;
        }
        
        /* Selectbox para a Aba 3 */
        .stSelectbox>div>div>div {
            border-radius: 8px !important;
            border: 1px solid #CBD5E1 !important;
            padding: 2px 8px !important;
        }

        /* ===== BOTÕES PRIMÁRIOS ===== */
        button[kind="primary"] {
            border-radius: 8px !important;
            background-color: #0F766E !important;
            color: white !important;
            border: none !important;
            transition: all 0.2s ease;
            font-weight: 600 !important;
            padding: 10px 0 !important;
        }
        button[kind="primary"]:hover {
            background-color: #115E59 !important;
            transform: translateY(-2px);
        }

        /* ===== BOTÃO SECUNDÁRIO (Botão Limpar Histórico) ===== */
        button[kind="secondary"] {
            background-color: transparent !important;
            border: 1px solid #CBD5E1 !important;
            color: #64748B !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            transition: all 0.2s ease !important;
            padding: 10px 0 !important;
        }
        button[kind="secondary"]:hover {
            border-color: #EF4444 !important;
            color: #EF4444 !important;
            background-color: #FEF2F2 !important;
        }

        /* ===== ÍCONES FLUTUANTES (ESTRELA E X) ===== */
        button[title="Favoritar"], button[title="Remover do histórico"] {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            height: auto !important;
            line-height: 1 !important;
            margin-top: -5px !important;
        }
        button[title="Favoritar"] {
            color: #F59E0B !important;
            font-size: 1.8rem !important;
        }
        button[title="Favoritar"]:hover {
            transform: scale(1.15);
            color: #D97706 !important;
            background: transparent !important;
            border: none !important;
        }
        button[title="Remover do histórico"] {
            color: #94A3B8 !important;
            font-size: 1.2rem !important;
            margin-top: 0 !important;
        }
        button[title="Remover do histórico"]:hover {
            transform: scale(1.15);
            color: #EF4444 !important;
            background: transparent !important;
            border: none !important;
        }

        /* ===== CARDS DE RESULTADOS E SETINHA (EXPANDER) ===== */
        [data-testid="stVerticalBlock"] > [style*="flex-direction: column"] > [data-testid="stVerticalBlock"] {
            background: white !important;
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid #E2E8F0 !important;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
            margin-bottom: 1.5rem;
        }
        [data-testid="stVerticalBlock"] p {
            color: #1E293B !important;
        }
        
        [data-testid="stExpander"] {
            background-color: #F8FAFC !important;
            border: 1px solid #E2E8F0 !important;
            border-left: 5px solid #0F766E !important;
            border-radius: 8px !important;
            margin-top: 1rem !important;
            box-shadow: none !important;
        }
        [data-testid="stExpander"] summary {
            padding: 0.8rem 1rem !important;
            color: #0F172A !important;
            font-weight: 600 !important;
            background: transparent !important;
        }
        [data-testid="stExpander"] summary:hover {
            color: #0F766E !important;
        }
        [data-testid="stExpanderDetails"] {
            padding: 1rem 1.5rem !important;
            padding-top: 0.5rem !important;
        }

        hr {
            border-color: #E2E8F0 !important;
            margin-top: 2rem;
            margin-bottom: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# ===== SESSION STATE =====
if "resultados_busca" not in st.session_state: st.session_state.resultados_busca = None
if "data" not in st.session_state: st.session_state.data = None
if "historico" not in st.session_state: st.session_state.historico = []
if "resultados_livros" not in st.session_state: st.session_state.resultados_livros = None
if "ultima_busca_artigo" not in st.session_state: st.session_state.ultima_busca_artigo = ""
if "ultima_busca_livro" not in st.session_state: st.session_state.ultima_busca_livro = ""
if "ref_manual" not in st.session_state: st.session_state.ref_manual = None

# Migração do histórico
historico_migrado = []
for item in st.session_state.historico:
    if isinstance(item, str): historico_migrado.append({"ref": item, "url": ""})
    else: historico_migrado.append(item)
st.session_state.historico = historico_migrado

# ===== FUNÇÕES DE CALLBACK =====
def toggle_historico(ref_str, url_str):
    existe = any(i.get('ref') == ref_str for i in st.session_state.historico)
    if existe:
        st.session_state.historico = [i for i in st.session_state.historico if i.get('ref') != ref_str]
        st.toast("🗑️ Referência removida do histórico!")
    else:
        st.session_state.historico.append({'ref': ref_str, 'url': url_str})
        st.toast("⭐ Referência salva com sucesso!")

def remover_do_historico(ref_str):
    st.session_state.historico = [i for i in st.session_state.historico if i.get('ref') != ref_str]
    st.toast("🗑️ Referência removida do histórico!")

# ===== FUNÇÕES DE TRATAMENTO AUTOMÁTICAS =====
def listar_todos_autores(data):
    autores = data.get("author", [])
    if not autores: autores = data.get("editor", [])
    nomes = []
    for a in autores:
        nome = a.get("given", "")
        sobrenome = a.get("family", "")
        if nome and sobrenome: nomes.append(f"{nome} {sobrenome}")
        elif sobrenome: nomes.append(sobrenome)
    return ", ".join(nomes) if nomes else "Autor desconhecido"

def gerar_citacao(data):
    autores = data.get("author", [])
    if not autores: autores = data.get("editor", [])
    data_parts = data.get("issued", {}).get("date-parts", [[None]])
    ano = str(data_parts[0][0]) if len(data_parts[0]) > 0 and data_parts[0][0] is not None else "[s.d.]"
    if not autores: return f"(Autor desconhecido, {ano})"
    nomes = []
    for a in autores:
        sobrenome = a.get("family", "")
        if sobrenome: nomes.append(sobrenome.title())
    if len(nomes) == 0: return f"(Autor desconhecido, {ano})"
    elif len(nomes) <= 3: return f"({'; '.join(nomes)}, {ano})"
    else: return f"({nomes[0]} et al., {ano})"

def gerar_referencia(data):
    tipo = data.get("type", "")
    def extrair_autores(lista_autores):
        autores_formatados = []
        for autor in lista_autores:
            sobrenome = autor.get("family", "")
            nome = autor.get("given", "")
            if sobrenome:
                iniciais = " ".join([n[0].upper() + "." for n in nome.split() if n])
                autores_formatados.append(f"{sobrenome.upper()}, {iniciais}")
        if len(autores_formatados) >= 4: return autores_formatados[0] + " et al."
        elif len(autores_formatados) > 0: return "; ".join(autores_formatados).rstrip(".")
        return "AUTOR DESCONHECIDO"
        
    def pegar_volume(dados):
        vol = dados.get("volume", "")
        if not vol: vol = dados.get("collection-number", "")
        if not vol: vol = dados.get("issue", "")
        if isinstance(vol, list) and vol: return str(vol[0])
        return str(vol) if vol else ""

    autores_str = extrair_autores(data.get("author", []))
    titulo = data.get("title", ["Sem título"])[0].strip()
    tags_remover = ["<i>", "</i>", "<I>", "</I>", "<italic>", "</italic>", "<ITALIC>", "</ITALIC>", "<em>", "</em>", "&lt;i&gt;", "&lt;/i&gt;"]
    for tag in tags_remover: titulo = titulo.replace(tag, "*")
    if titulo and titulo[-1] not in ["?", "!", "."]: titulo += "."
    data_parts = data.get("issued", {}).get("date-parts", [[None]])
    ano = str(data_parts[0][0]) if len(data_parts[0]) > 0 and data_parts[0][0] is not None else "[s.d.]"
    editora = data.get("publisher", "[s.n.]")
    paginas = data.get("page", "")

    if tipo in ["book", "proceedings"]:
        autores_finais = autores_str
        if autores_finais == "AUTOR DESCONHECIDO":
            editores_str = extrair_autores(data.get("editor", []))
            if editores_str != "AUTOR DESCONHECIDO":
                if ";" in editores_str or "et al." in editores_str: autores_finais = f"{editores_str} (Eds.)"
                else: autores_finais = f"{editores_str} (Ed.)"
        cidade = data.get("publisher-location", "[s.l.]")
        volume = pegar_volume(data)
        subtitulo = data.get("subtitle", [""])[0] if data.get("subtitle") else ""
        ref = f"{autores_finais.rstrip('.')}. *{titulo.rstrip('.')}*"
        if subtitulo: ref += f": {subtitulo}"
        ref += f". {cidade}: {editora}, {ano}."
        if volume: ref += f" v. {volume}."
        return ref

    elif tipo == "book-chapter":
        editores_str = extrair_autores(data.get("editor", []))
        container_titles = data.get("container-title", [])
        livro_titulo = ""
        serie = ""
        if len(container_titles) > 1: livro_titulo, serie = container_titles[0], container_titles[1]
        elif len(container_titles) == 1: livro_titulo = container_titles[0]
        else: livro_titulo = "Sem título do livro"
        ref = f"{autores_str.rstrip('.')}. {titulo} *In*: "
        if editores_str != "AUTOR DESCONHECIDO": ref += f"{editores_str} (Ed.). "
        ref += f"*{livro_titulo}*. "
        if serie: ref += f"{serie}. "
        cidade = data.get("publisher-location", "[s.l.]")
        ref += f"{cidade}: {editora}, {ano}."
        volume = pegar_volume(data)
        if volume: ref += f" v. {volume}."
        if paginas: ref += f" p. {paginas}."
        return ref

    elif tipo in ["proceedings-article", "paper-conference"]:
        nome_evento = data.get("container-title", data.get("event", {}).get("name", ["Anais do Evento"]))
        if isinstance(nome_evento, list): nome_evento = nome_evento[0]
        ref = f"{autores_str.rstrip('.')}. {titulo} *In*: {nome_evento.upper()}, {ano}. *Anais* [...]. [s.l.]: {editora}, {ano}."
        if paginas: ref += f" p. {paginas}."
        return ref

    else:
        journal = data.get("container-title", [""])[0]
        numero = data.get("issue", "")
        volume = pegar_volume(data) 
        if isinstance(numero, list) and numero: numero = str(numero[0])
        ref = f"{autores_str.rstrip('.')}. {titulo}"
        if journal: ref += f" *{journal}*"
        if volume: ref += f", v. {volume}"
        if numero: ref += f", n. {numero}"
        if paginas: ref += f", p. {paginas}"
        mes = data_parts[0][1] if len(data_parts[0]) > 1 else ""
        meses = ["jan.", "fev.", "mar.", "abr.", "maio", "jun.", "jul.", "ago.", "set.", "out.", "nov.", "dez."]
        mes_formatado = meses[mes-1] if mes and isinstance(mes, int) and mes <= 12 else ""
        if mes_formatado: ref += f", {mes_formatado} {ano}."
        else: ref += f", {ano}."
        return ref

def gerar_referencia_livro(livro):
    titulo = livro.get("titulo", "Sem título").strip()
    subtitulo = livro.get("subtitulo", "").strip()
    autores = livro.get("autores", [])
    autores_formatados = []
    for nome_completo in autores:
        partes = nome_completo.split()
        if partes:
            sobrenome = partes[-1].upper()
            nome = " ".join(partes[:-1])
            iniciais = " ".join([n[0].upper() + "." for n in nome.split() if n])
            autores_formatados.append(f"{sobrenome}, {iniciais}")
    if len(autores_formatados) >= 4: autores_str = autores_formatados[0] + " et al."
    elif len(autores_formatados) > 0: autores_str = "; ".join(autores_formatados)
    else: autores_str = "AUTOR DESCONHECIDO"
    editora = livro.get("editora", "[s.n.]")
    cidade = "[s.l.]" 
    ano = livro.get("ano", "[s.d.]")
    titulo_formatado = f"*{titulo}*"
    if subtitulo: referencia = f"{autores_str.rstrip('.')}. {titulo_formatado}: {subtitulo}. {cidade}: {editora}, {ano}."
    else: referencia = f"{autores_str.rstrip('.')}. {titulo_formatado}. {cidade}: {editora}, {ano}."
    return referencia

# ===== CABEÇALHO DO APP =====
st.markdown("""
    <div style='text-align: center; margin-bottom: 3rem;'>
        <h1 style='font-size: 3rem; margin-bottom: 0.5rem;'>CiteFix</h1>
        <p style='color: #64748B; font-size: 1.1rem; margin-top: 0;'>A precisão acadêmica que o seu trabalho exige.</p>
    </div>
""", unsafe_allow_html=True)

# ===== CRIAÇÃO DAS ABAS =====
tab_artigos, tab_livros, tab_manual, tab_historico = st.tabs([
    "Artigos Científicos", 
    "Livros", 
    "Gerador Manual", 
    "Histórico"
])

# ===== ABA 1: ARTIGOS =====
with tab_artigos:
    st.markdown("### Busca de Artigos")
    
    entrada = st.text_input("Busca", placeholder="Cole o DOI ou digite o Título e aperte Enter...", label_visibility="collapsed", key="in_art")

    if entrada and entrada != st.session_state.ultima_busca_artigo:
        st.session_state.ultima_busca_artigo = entrada
        st.session_state.resultados_busca = None
        st.session_state.data = None

        with st.spinner('Pesquisando na base de dados...'):
            if "/" in entrada:
                url = f"https://api.crossref.org/works/{entrada}"
                response = requests.get(url)
                if response.status_code == 200:
                    st.session_state.data = response.json()["message"]
                else:
                    st.warning("Não foi possível encontrar este DOI.")
            else:
                url = f"https://api.crossref.org/works?query.title={entrada}&rows=5"
                response = requests.get(url)
                if response.status_code == 200:
                    resultados = response.json()["message"]["items"]
                    if not resultados:
                        st.warning("Nenhum artigo encontrado com este título.")
                    else:
                        st.session_state.resultados_busca = resultados
                else:
                    st.error("Falha na comunicação com a base de dados.")

    # ===== RESULTADO EXATO (DOI) =====
    if st.session_state.data and not st.session_state.resultados_busca:
        data = st.session_state.data
        titulo_item = data.get("title", ["Sem título"])[0].strip()
        titulo_item = titulo_item.replace("<i>", "*").replace("</i>", "*").replace("<I>", "*").replace("</I>", "*").replace("<italic>", "*").replace("</italic>", "*").replace("<ITALIC>", "*").replace("</ITALIC>", "*").replace("<em>", "*").replace("</em>", "*").replace("&lt;i&gt;", "*").replace("&lt;/i&gt;", "*")
        titulo_html = re.sub(r'\*(.*?)\*', r'<i>\1</i>', titulo_item)
        data_parts = data.get("issued", {}).get("date-parts", [[None]])
        ano = str(data_parts[0][0]) if len(data_parts[0]) > 0 and data_parts[0][0] is not None else "[s.d.]"
        autores_completos = listar_todos_autores(data)
        doi_str = data.get("DOI", "Não disponível")
        url_link = data.get("URL", f"https://doi.org/{doi_str}" if doi_str != "Não disponível" else "")

        st.markdown(f"#### Resultado Encontrado")
        
        with st.container():
            st.markdown(f"<p style='margin-bottom: 2px; font-weight: 600; color: #1E293B;'>{titulo_html}</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: #64748B; font-size: 0.9em; line-height: 1.4; margin-bottom: 5px;'><b>Autores:</b> {autores_completos}<br><b>Ano:</b> {ano}<br><b>DOI:</b> {doi_str}</p>", unsafe_allow_html=True)

            citacao = gerar_citacao(data)
            ref = gerar_referencia(data)

            with st.expander("Ver Referência", expanded=True):
                c_text, c_icons = st.columns([85, 15], vertical_alignment="top")
                with c_text:
                    st.markdown(f"**Citação no texto:** {citacao}\n\n**Referência Formatada:**\n\n{ref}")
                with c_icons:
                    c_star, c_link = st.columns(2, vertical_alignment="top")
                    with c_star:
                        is_saved = any(i.get('ref') == ref for i in st.session_state.historico)
                        st.button("★" if is_saved else "☆", key="star_doi", help="Favoritar", type="secondary", on_click=toggle_historico, args=(ref, url_link))
                    with c_link:
                        if url_link:
                            st.markdown(f"<div style='text-align: center; margin-top: -2px;'><a href='{url_link}' target='_blank' style='text-decoration:none; font-size:1.4rem; color:#64748B;' title='Acessar Documento'>🔗</a></div>", unsafe_allow_html=True)

    # ===== LISTA DE RESULTADOS (ARTIGOS) =====
    if st.session_state.resultados_busca:
        st.markdown("<br><h4>Resultados Encontrados</h4>", unsafe_allow_html=True)
        
        for idx, item in enumerate(st.session_state.resultados_busca):
            with st.container():
                titulo_item = item.get("title", ["Sem título"])[0].strip()
                titulo_item = titulo_item.replace("<i>", "*").replace("</i>", "*").replace("<I>", "*").replace("</I>", "*").replace("<italic>", "*").replace("</italic>", "*").replace("<ITALIC>", "*").replace("</ITALIC>", "*").replace("<em>", "*").replace("</em>", "*").replace("&lt;i&gt;", "*").replace("&lt;/i&gt;", "*")
                titulo_html = re.sub(r'\*(.*?)\*', r'<i>\1</i>', titulo_item)
                data_parts = item.get("issued", {}).get("date-parts", [[None]])
                ano = str(data_parts[0][0]) if len(data_parts[0]) > 0 and data_parts[0][0] is not None else "[s.d.]"
                autores_completos = listar_todos_autores(item)
                doi_str = item.get("DOI", "Não disponível")
                url_link = item.get("URL", f"https://doi.org/{doi_str}" if doi_str != "Não disponível" else "")

                st.markdown(f"<p style='margin-bottom: 2px; font-weight: 600; color: #1E293B;'>{titulo_html}</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='color: #64748B; font-size: 0.9em; line-height: 1.4; margin-bottom: 5px;'><b>Autores:</b> {autores_completos}<br><b>Ano:</b> {ano}<br><b>DOI:</b> {doi_str}</p>", unsafe_allow_html=True)

                with st.expander("Ver Referência"):
                    citacao = gerar_citacao(item)
                    ref = gerar_referencia(item)
                    
                    c_text, c_icons = st.columns([85, 15], vertical_alignment="top")
                    with c_text:
                        st.markdown(f"**Citação no texto:** {citacao}\n\n**Referência Formatada:**\n\n{ref}")
                    with c_icons:
                        c_star, c_link = st.columns(2, vertical_alignment="top")
                        with c_star:
                            is_saved = any(i.get('ref') == ref for i in st.session_state.historico)
                            st.button("★" if is_saved else "☆", key=f"star_art_{idx}", help="Favoritar", type="secondary", on_click=toggle_historico, args=(ref, url_link))
                        with c_link:
                            if url_link:
                                st.markdown(f"<div style='text-align: center; margin-top: -2px;'><a href='{url_link}' target='_blank' style='text-decoration:none; font-size:1.4rem; color:#64748B;' title='Acessar Documento'>🔗</a></div>", unsafe_allow_html=True)

# ===== ABA 2: LIVROS =====
with tab_livros:
    st.markdown("### Busca de Livros")
    
    entrada_livro = st.text_input("Busca", placeholder="Digite o Título, Autor ou ISBN e aperte Enter...", label_visibility="collapsed", key="in_livro")

    if entrada_livro and entrada_livro != st.session_state.ultima_busca_livro:
        st.session_state.ultima_busca_livro = entrada_livro
        st.session_state.resultados_livros = None

        with st.spinner('Procurando nos acervos...'):
            livros_encontrados = []
            try:
                url_google = "https://www.googleapis.com/books/v1/volumes"
                params_g = {"q": entrada_livro, "maxResults": 5, "key": st.secrets["GOOGLE_API_KEY"], "country": "BR"} 
                resp_g = requests.get(url_google, params=params_g, timeout=5)
                if resp_g.status_code == 200:
                    for item in resp_g.json().get("items", []):
                        info = item.get("volumeInfo", {})
                        livros_encontrados.append({
                            "id": item.get("id", "g_desc"),
                            "titulo": info.get("title", "Sem título"),
                            "subtitulo": info.get("subtitle", ""),
                            "autores": info.get("authors", []),
                            "editora": info.get("publisher", "[s.n.]"),
                            "ano": str(info.get("publishedDate", "[s.d.]"))[:4],
                            "fonte": "Google Books",
                            "url": info.get("infoLink", "")
                        })
            except Exception: pass 

            try:
                url_ol = "https://openlibrary.org/search.json"
                params_ol = {"q": entrada_livro, "limit": 5}
                resp_ol = requests.get(url_ol, params=params_ol, timeout=8)
                if resp_ol.status_code == 200:
                    for doc in resp_ol.json().get("docs", []):
                        editora_ol = doc.get("publisher", ["[s.n.]"])[0] if doc.get("publisher") else "[s.n.]"
                        livros_encontrados.append({
                            "id": str(doc.get("key", "ol_desc")),
                            "titulo": doc.get("title", "Sem título"),
                            "subtitulo": "",
                            "autores": doc.get("author_name", []),
                            "editora": editora_ol,
                            "ano": str(doc.get("first_publish_year", "[s.d.]")),
                            "fonte": "OpenLibrary",
                            "url": f"https://openlibrary.org{doc.get('key', '')}"
                        })
            except Exception: pass

            if livros_encontrados:
                st.session_state.resultados_livros = livros_encontrados
            else:
                st.warning("Nenhum livro encontrado. Verifique os termos da busca.")

    # ===== EXIBIÇÃO DOS LIVROS =====
    if st.session_state.resultados_livros:
        st.markdown("<br><h4>Resultados Encontrados</h4>", unsafe_allow_html=True)

        for idx, item in enumerate(st.session_state.resultados_livros):
            with st.container():
                titulo_item = item.get("titulo", "Sem título")
                titulo_html = re.sub(r'\*(.*?)\*', r'<i>\1</i>', titulo_item)
                autores = item.get("autores", ["Autor desconhecido"])
                autores_str = ", ".join(autores)
                ano_pub = item.get("ano", "[s.d.]")
                fonte = item.get("fonte", "")
                url_link = item.get("url", "")

                st.markdown(f"<p style='margin-bottom: 2px; font-weight: 600; color: #1E293B;'>{titulo_html}</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='color: #64748B; font-size: 0.9em; line-height: 1.4; margin-bottom: 5px;'><b>Autores:</b> {autores_str}<br><b>Ano:</b> {ano_pub}<br><b>Base:</b> {fonte}</p>", unsafe_allow_html=True)

                with st.expander("Ver Referência"):
                    ref_livro = gerar_referencia_livro(item)
                    
                    c_text, c_icons = st.columns([85, 15], vertical_alignment="top")
                    with c_text:
                        st.markdown(f"**Referência Formatada:**\n\n{ref_livro}")
                    with c_icons:
                        c_star, c_link = st.columns(2, vertical_alignment="top")
                        with c_star:
                            is_saved = any(i.get('ref') == ref_livro for i in st.session_state.historico)
                            st.button("★" if is_saved else "☆", key=f"star_livro_{idx}", help="Favoritar", type="secondary", on_click=toggle_historico, args=(ref_livro, url_link))
                        with c_link:
                            if url_link:
                                st.markdown(f"<div style='text-align: center; margin-top: -2px;'><a href='{url_link}' target='_blank' style='text-decoration:none; font-size:1.4rem; color:#64748B;' title='Acessar Livro'>🔗</a></div>", unsafe_allow_html=True)

# ===== ABA 3: MANUAL =====
with tab_manual:
    st.markdown("### Gerador de Trabalhos Acadêmicos")
    st.markdown("<p style='color: #64748B; font-size: 0.95em; margin-bottom: 2rem;'>Preencha os dados para gerar referências impecáveis de Monografias, TCCs, Dissertações e Teses, que normalmente não possuem DOI.</p>", unsafe_allow_html=True)
    
    with st.form("form_tcc"):
        col1, col2 = st.columns(2)
        with col1:
            autor_m = st.text_input("Autor (Nome Completo)", placeholder="Ex: Ana Maria da Silva")
            titulo_m = st.text_input("Título do Trabalho", placeholder="Ex: O impacto da inteligência artificial na educação")
            tipo_m = st.selectbox("Tipo de Documento", ["Trabalho de Conclusão de Curso", "Dissertação", "Tese", "Monografia"])
        with col2:
            curso_m = st.text_input("Grau e Curso", placeholder="Ex: Bacharelado em Ciência da Computação")
            inst_m = st.text_input("Instituição", placeholder="Ex: Universidade de São Paulo")
            cidade_m = st.text_input("Cidade", placeholder="Ex: São Paulo")
            ano_m = st.text_input("Ano da Defesa", placeholder="Ex: 2024")
            
        submit_manual = st.form_submit_button("Gerar Referência ABNT", type="primary", use_container_width=True)
        
    if submit_manual:
        if autor_m and titulo_m and ano_m:
            partes = autor_m.strip().split()
            if len(partes) > 1:
                sobrenome = partes[-1].upper()
                iniciais = " ".join([n[0].upper() + "." for n in partes[:-1]])
                autor_fmt = f"{sobrenome}, {iniciais}"
                cit_fmt = f"{partes[-1].title()}"
            else:
                autor_fmt = autor_m.upper()
                cit_fmt = autor_m.title()
            
            ref_manual_txt = f"{autor_fmt}. *{titulo_m.rstrip('.')}*. {ano_m}. {tipo_m} ({curso_m}) - {inst_m}, {cidade_m}, {ano_m}."
            citacao_manual_txt = f"({cit_fmt}, {ano_m})"
            
            st.session_state.ref_manual = ref_manual_txt
            st.session_state.cit_manual = citacao_manual_txt
        else:
            st.warning("Preencha pelo menos o Autor, Título e Ano para gerar a referência.")
            
    if st.session_state.ref_manual:
        st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
        with st.expander("Ver Referência Gerada", expanded=True):
            c_text, c_icons = st.columns([85, 15], vertical_alignment="top")
            with c_text:
                st.markdown(f"**Citação no texto:** {st.session_state.cit_manual}\n\n**Referência Formatada:**\n\n{st.session_state.ref_manual}")
            with c_icons:
                c_star, c_link = st.columns(2, vertical_alignment="top")
                with c_star:
                    is_saved = any(i.get('ref') == st.session_state.ref_manual for i in st.session_state.historico)
                    st.button("★" if is_saved else "☆", key="star_manual", help="Favoritar", type="secondary", on_click=toggle_historico, args=(st.session_state.ref_manual, ""))

# ===== ABA 4: HISTÓRICO =====
with tab_historico:
    # O botão de limpar histórico agora ocupa o lado direito e tem uma lixeira
    col_titulo, col_limpar = st.columns([7.5, 2.5], vertical_alignment="bottom")
    
    with col_titulo:
        st.markdown("### Repositório de Referências")
        
    if st.session_state.historico:
        with col_limpar:
            if st.button("🗑️ Limpar Histórico", type="secondary", use_container_width=True):
                st.session_state.historico = []
                st.session_state.limpou_tudo = True
                st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)
        historico_ordenado = sorted(st.session_state.historico, key=lambda x: x['ref'].lower())

        for i, item in enumerate(historico_ordenado):
            ref_str = item.get('ref', '')
            url_str = item.get('url', '')
            with st.container():
                col_texto, col_link, col_botao_del = st.columns([85, 8, 7], vertical_alignment="center")
                with col_texto:
                    ref_html = re.sub(r'\*(.*?)\*', r'<i>\1</i>', ref_str)
                    st.markdown(f"<div style='padding: 10px; background: white; border-radius: 8px; border: 1px solid #E2E8F0; line-height: 1.5;'>{ref_html}</div>", unsafe_allow_html=True)
                with col_link:
                    if url_str:
                        st.markdown(f"<div style='text-align: center;'><a href='{url_str}' target='_blank' style='text-decoration:none; font-size:1.4rem; color:#64748B;' title='Acessar Documento'>🔗</a></div>", unsafe_allow_html=True)
                with col_botao_del:
                    st.button("✕", key=f"del_hist_{i}", help="Remover do histórico", type="secondary", on_click=remover_do_historico, args=(ref_str,))
                st.write("") 
    else:
        st.info("Seu histórico de trabalho está vazio. Suas referências salvas aparecerão aqui.")
