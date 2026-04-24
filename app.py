"""
Aplicação Streamlit para Dashboard de Cidades Inteligentes com foco em segurança.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página (Deve ser o primeiro comando do Streamlit)
st.set_page_config(page_title="Ranking de Cidades - Segurança", layout="wide", initial_sidebar_state="expanded")

# =====================================================================
# CARREGAMENTO DE DADOS (COM CACHE E RESILIÊNCIA)
# =====================================================================
@st.cache_data
def load_data():
    """Carrega os dados do CSV de forma otimizada e segura."""
    try:
        return pd.read_csv("ranking_seguranca_cidades.csv")
    except FileNotFoundError:
        st.error("🚨 Erro crítico: Arquivo 'ranking_seguranca_cidades.csv' não encontrado. Verifique o pipeline de ETL.")
        st.stop() # Interrompe a execução graciosamente

df = load_data()

# =====================================================================
# CABEÇALHO DA APLICAÇÃO
# =====================================================================
st.title("🛡️ Ranking de Cidades Inteligentes: Foco em Segurança")
st.markdown("Dashboard analítico para identificar os municípios com melhor infraestrutura e indicadores de segurança.")
st.divider()

# =====================================================================
# BARRA LATERAL (FILTROS)
# =====================================================================
st.sidebar.header("⚙️ Filtros de Análise")

# Filtro de Estado
estados_disponiveis = sorted(df['Estado'].unique())
estados_selecionados = st.sidebar.multiselect("Selecione os Estados:", estados_disponiveis, default=[])

# Filtro de Top N Cidades
top_n = st.sidebar.slider("Mostrar Top N cidades:", min_value=5, max_value=50, value=10, step=5)

# Aplicação dos filtros de forma dinâmica
if estados_selecionados:
    df_filtrado = df[df['Estado'].isin(estados_selecionados)]
else:
    df_filtrado = df.copy()

df_top_n = df_filtrado.head(top_n)

# =====================================================================
# ÁREA PRINCIPAL: KPIs E GRÁFICOS
# =====================================================================
if not df_top_n.empty:
    
    # --- MÉTRICAS (KPIs) ---
    col1, col2, col3 = st.columns(3)
    melhor_cidade = df_top_n.iloc[0]
    
    col1.metric("🏆 Melhor Cidade (Seleção)", f"{melhor_cidade['Cidade']} ({melhor_cidade['Estado']})", f"Score: {melhor_cidade['Score_Seguranca']:.1f}")
    col2.metric("📊 Média do Score (Seleção)", f"{df_filtrado['Score_Seguranca'].mean():.1f}")
    col3.metric("🏙️ Cidades Analisadas", len(df_filtrado))

    st.markdown("<br>", unsafe_allow_html=True) # Espaçamento

    # --- GRÁFICO DE RANKING ---
    st.subheader(f"Top {top_n} Cidades Mais Seguras")
    
    # Plotly para alta interatividade com baixo custo
    fig = px.bar(
        df_top_n.sort_values('Score_Seguranca', ascending=True), 
        x='Score_Seguranca', 
        y='Cidade', 
        orientation='h',
        color='Score_Seguranca',
        color_continuous_scale='Blues',
        text_auto='.1f',
        hover_data=['Estado', 'População total estimada do município']
    )
    
    fig.update_layout(
        xaxis_title="Score de Segurança (0-100)", 
        yaxis_title="Cidade",
        margin=dict(l=0, r=0, t=30, b=0) # Otimização de espaço na tela
    )
    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("Nenhuma cidade encontrada com os filtros atuais.")

# =====================================================================
# ÁREA DE DADOS BRUTOS E EXPORTAÇÃO
# =====================================================================
st.divider()
col_tabela, col_botao = st.columns([4, 1])

with col_tabela:
    with st.expander("Ver Tabela de Dados Completa"):
        st.dataframe(df_top_n)

with col_botao:
    # Feature de SRE/Data: Permitir que o usuário baixe o dado que ele mesmo filtrou
    csv_export = df_top_n.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar Dados Filtrados",
        data=csv_export,
        file_name='cidades_filtradas.csv',
        mime='text/csv',
    )