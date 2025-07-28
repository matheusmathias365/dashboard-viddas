
import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
st.set_page_config(
    layout="wide",
    page_title="Dashboard de Estatísticas da Clínica"
)

# --- Funções Auxiliares ---
@st.cache_data
def carregar_dados_consolidados(caminho_arquivo):
    """Carrega os dados do arquivo CSV consolidado."""
    try:
        df = pd.read_csv(caminho_arquivo, sep=';')
        # Converter a coluna de data para o formato datetime
        df['Data'] = pd.to_datetime(df['Data'])
        # GARANTIR que a coluna 'Procedimento' seja do tipo string
        df['Procedimento'] = df['Procedimento'].astype(str).str.strip().str.upper()
        df['Cliente'] = df['Cliente'].str.strip().str.upper()
        return df
    except FileNotFoundError:
        st.error(f"Arquivo de estatísticas não encontrado em: {caminho_arquivo}")
        return None
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo CSV: {e}")
        return None

# --- Carregamento dos Dados ---
ARQUIVO_DADOS = 'estatisticas_consolidadas_clinica.csv'
df = carregar_dados_consolidados(ARQUIVO_DADOS)

if df is None:
    st.stop() # Interrompe a execução se os dados não puderem ser carregados

# --- Título Principal ---
st.title("Dashboard de Análise de Atendimentos")
st.markdown("Análise interativa dos dados de atendimentos consolidados.")

# --- Barra Lateral (Sidebar) com Filtros ---
st.sidebar.header("Filtros de Análise")

# Filtro de Ano
anos_disponiveis = sorted(df['Ano'].unique(), reverse=True)
anos_selecionados = st.sidebar.multiselect(
    'Selecione o(s) Ano(s)',
    anos_disponiveis,
    default=anos_disponiveis
)

# Filtro de Mês
meses_disponiveis = sorted(df['Mes'].unique())
meses_selecionados = st.sidebar.multiselect(
    'Selecione o(s) Mês(es)',
    meses_disponiveis,
    default=meses_disponiveis
)

# Filtro de Procedimento
procedimentos_disponiveis = sorted(df['Procedimento'].unique())
procedimentos_selecionados = st.sidebar.multiselect(
    'Selecione o(s) Procedimento(s)',
    procedimentos_disponiveis,
    default=procedimentos_disponiveis
)

# Filtro de Cliente (Convênio)
clientes_disponiveis = sorted(df['Cliente'].unique())
clientes_selecionados = st.sidebar.multiselect(
    'Selecione o(s) Tipo(s) de Cliente',
    clientes_disponiveis,
    default=clientes_disponiveis
)

# --- Filtrando o DataFrame com base nas seleções ---
df_filtrado = df[
    (df['Ano'].isin(anos_selecionados)) &
    (df['Mes'].isin(meses_selecionados)) &
    (df['Procedimento'].isin(procedimentos_selecionados)) &
    (df['Cliente'].isin(clientes_selecionados))
]

# --- Área Principal ---
if df_filtrado.empty:
    st.warning("Nenhum dado encontrado para os filtros selecionados.")
else:
    # KPIs (Indicadores Chave de Performance)
    st.header("Resumo dos Dados Filtrados")
    total_quantidade = df_filtrado['Quantidade'].sum()
    num_registros = len(df_filtrado)

    col1, col2 = st.columns(2)
    col1.metric("Total de Procedimentos Realizados", f"{total_quantidade:,}")
    col2.metric("Número de Registros Analisados", f"{num_registros:,}")

    st.markdown("---")

    # --- Gráficos ---
    st.header("Visualizações Gráficas")
    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:
        # Gráfico 1: Evolução da Quantidade ao Longo do Tempo
        st.subheader("Evolução de Atendimentos")
        df_evolucao = df_filtrado.groupby('Data')['Quantidade'].sum().reset_index()
        fig_evolucao = px.line(
            df_evolucao,
            x='Data',
            y='Quantidade',
            title='Quantidade de Atendimentos ao Longo do Tempo',
            labels={'Data': 'Data', 'Quantidade': 'Quantidade'}
        )
        st.plotly_chart(fig_evolucao, use_container_width=True)

        # Gráfico 2: Top 10 Procedimentos
        st.subheader("Procedimentos Mais Frequentes")
        df_top_proc = df_filtrado.groupby('Procedimento')['Quantidade'].sum().nlargest(10).reset_index()
        fig_top_proc = px.bar(
            df_top_proc.sort_values('Quantidade'),
            x='Quantidade',
            y='Procedimento',
            orientation='h',
            title='Top 10 Procedimentos por Quantidade',
            labels={'Quantidade': 'Quantidade Total', 'Procedimento': 'Procedimento'}
        )
        st.plotly_chart(fig_top_proc, use_container_width=True)

    with col_graf2:
        # Gráfico 3: Distribuição por Tipo de Cliente
        st.subheader("Distribuição por Tipo de Cliente")
        df_cliente = df_filtrado.groupby('Cliente')['Quantidade'].sum().reset_index()
        fig_cliente = px.pie(
            df_cliente,
            names='Cliente',
            values='Quantidade',
            title='Distribuição de Atendimentos por Cliente',
            hole=0.4
        )
        st.plotly_chart(fig_cliente, use_container_width=True)

    # --- Tabela de Dados Detalhada ---
    st.markdown("---")
    st.header("Dados Detalhados Filtrados")
    # Exibir um subconjunto das colunas para clareza
    st.dataframe(df_filtrado[['Ano', 'Mes', 'Cliente', 'Procedimento', 'Quantidade', 'Data']], use_container_width=True)

# --- Rodapé ---
st.sidebar.markdown("---")
st.sidebar.info("Dashboard criado a partir de dados consolidados.")
