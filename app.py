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

st.title("CiteFix - Gerador de Referências")

# ===== FORM =====
with st.form("form_busca"):
	entrada = st.text_input("Digite o DOI OU o título do artigo:")
	submit = st.form_submit_button("Buscar")

# ===== BUSCA =====
if submit:
	st.session_state.resultados_busca = None
	st.session_state.data = None
	st.session_state.selecionado = None

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

# ===== FUNÇÃO DE GERAR REFERÊNCIA =====
def gerar_referencia(data):

	titulo = data.get("title", ["Sem título"])[0]
	autores = data.get("author", [])
	data_parts = data.get("issued", {}).get("date-parts", [[None]])
	ano = data_parts[0][0]
	mes = data_parts[0][1] if len(data_parts[0]) > 1 else ""
	dia = data_parts[0][2] if len(data_parts[0]) > 2 else ""
	journal = data.get("container-title", [""])[0]

	meses = ["jan.", "fev.", "mar.", "abr.", "maio", "jun.", "jul.", "ago.", "set.", "out.", "nov.", "dez."]
	mes_formatado = meses[mes-1] if mes and mes <= 12 else ""

	volume = data.get("volume", "")
	numero = data.get("issue", "")
	paginas = data.get("page", "")

	journal_formatado = f"*{journal}*"

	autores_formatados = []
	for autor in autores:
		sobrenome = autor.get("family", "")
		nome = autor.get("given", "")
		iniciais = " ".join([n[0].upper() + "." for n in nome.split() if n])
		autores_formatados.append(f"{sobrenome.upper()}, {iniciais}")

	if len(autores_formatados) >= 4:
		autores_str = autores_formatados[0] + " et al."
	else:
		autores_str = "; ".join(autores_formatados).rstrip(".")

	if autores_str.endswith("et al."):
		referencia = f"{autores_str} {titulo}. {journal_formatado}"
	else:
		referencia = f"{autores_str}. {titulo}. {journal_formatado}"

	if volume:
		referencia += f", v. {volume}"

	if numero:
		referencia += f", n. {numero}"

	if paginas:
		paginas = paginas.strip()

		if "-" in paginas:
			referencia += f", p. {paginas}"
		else:
			referencia += f", {paginas}"

	if dia and mes_formatado:
		referencia += f", {dia} {mes_formatado} {ano}"
	elif mes_formatado:
		referencia += f", {mes_formatado} {ano}"
	else:
		referencia += f", {ano}"

	return referencia.rstrip(".") + "."

def gerar_citacao(autores, ano):
	if not autores:
		return f"(Autor desconhecido, {ano})"

	nomes = []

	for a in autores:
		sobrenome = a.get("family", "")
		if sobrenome:
			nomes.append(sobrenome.title())

	if len(nomes) <= 3:
		# até 3 autores: todos aparecem
		if len(nomes) == 1:
			return f"({nomes[0]}, {ano})"
		elif len(nomes) == 2:
			return f"({nomes[0]}; {nomes[1]}, {ano})"
		else:
			return f"({nomes[0]}; {nomes[1]};  {nomes[2]}, {ano})"

	else:
		# 4 ou mais: primeiro + et al.
		return f"({nomes[0]} et al., {ano})"

# ===== RESULTADO DOI =====
if st.session_state.data and not st.session_state.resultados_busca:

	data = st.session_state.data

	titulo_item = data.get("title", ["Sem título"])[0]

	autores = data.get("author", [])
	if autores:
		primeiro = autores[0]
		nome = f"{primeiro.get('family', '').upper()}, {primeiro.get('given', '').split()[0][0]}."
		autores_str = f"{nome} et al."
	else:
		autores_str = "Autor desconhecido"

	data_parts = data.get("issued", {}).get("date-parts", [[None]])
	ano = data_parts[0][0]

	st.write("### Resultado:")

	st.markdown(f"**{titulo_item}**")

	autores = data.get("author", [])
	data_parts = data.get("issued", {}).get("date-parts", [[None]])
	ano = data_parts[0][0]

	citacao = gerar_citacao(autores, ano)

	ref = gerar_referencia(data)

	st.markdown(f"**Citação no texto:** {citacao}")

	st.success(f"Referência:\n\n{ref}")

	if ref not in st.session_state.historico:
		st.session_state.historico.append(ref)

# ===== LISTA DE TÍTULOS =====
if st.session_state.resultados_busca:

	st.write("### Selecione o artigo correto:")

	for item in st.session_state.resultados_busca:
		titulo_item = item.get("title", ["Sem título"])[0]

		# autores
		autores = item.get("author", [])
		if autores:
			primeiro = autores[0]
			family = primeiro.get('family', '').upper()
			given = primeiro.get('given', '')

			inicial = given.split()[0][0] if given and given.split() else ""

			if family and inicial:
    			nome = f"{family}, {inicial}."
			elif family:
    			nome = family
			else:
    			nome = "Autor desconhecido"
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
			if ref not in st.session_state.historico:
				st.session_state.historico.append(ref)

		st.markdown("---")

# ===== MENSAGEM FINAL =====
if submit and not entrada:
	st.write("Digite um DOI ou título.")

st.write("## 📚 Histórico de Referências")

historico_ordenado = sorted(st.session_state.historico, key=str.lower)

for ref in historico_ordenado:
	st.markdown(ref)
	st.write("")  # espaço entre referências
