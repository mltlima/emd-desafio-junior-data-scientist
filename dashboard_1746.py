import streamlit as st
import pandas as pd
import plotly.express as px
import basedosdados as bd
from datetime import datetime, timedelta

# Configuração inicial
st.set_page_config(page_title="Dashboard Rio de Janeiro", layout="wide")

billing_project_id = "dados-rio-433101"

# Função para executar queries
@st.cache_data(ttl=3600)
def run_query(query):
  return bd.read_sql(query, billing_project_id=billing_project_id)

# Funções para obter dados específicos

@st.cache_data(ttl=3600)
def get_chamados_summary(data_inicio, data_fim):
  query = f"""
  SELECT 
      tipo as servico,
      status,
      DATE(data_inicio) as data,
      COUNT(*) as contagem
  FROM `datario.adm_central_atendimento_1746.chamado`
  WHERE data_inicio BETWEEN '{data_inicio}' AND '{data_fim}'
  GROUP BY tipo, status, DATE(data_inicio)
  """
  return run_query(query)

@st.cache_data(ttl=3600)
def get_bairros():
  query = "SELECT id_bairro, nome FROM `datario.dados_mestres.bairro`"
  return run_query(query)

@st.cache_data(ttl=3600)
def get_chamados_por_bairro(bairro_id):
  query = f"""
  SELECT 
      tipo,
      status,
      latitude,
      longitude
  FROM `datario.adm_central_atendimento_1746.chamado`
  WHERE id_bairro = '{bairro_id}'
  AND data_inicio >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
  """
  return run_query(query)

@st.cache_data(ttl=3600)
def get_eventos():
  query = """
  SELECT *
  FROM `datario.turismo_fluxo_visitantes.rede_hoteleira_ocupacao_eventos`
  WHERE data_inicial >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 YEAR)
  """
  return run_query(query)

@st.cache_data(ttl=3600)
def get_chamados_por_periodo(data_inicial, data_final):
  query = f"""
  SELECT 
      categoria,
      COUNT(*) as contagem
  FROM `datario.adm_central_atendimento_1746.chamado`
  WHERE data_inicio BETWEEN '{data_inicial}' AND '{data_final}'
  GROUP BY categoria
  """
  return run_query(query)

# Sidebar para seleção de dashboard
st.sidebar.title("Navegação")
dashboard_selection = st.sidebar.radio(
  "Escolha um dashboard:",
  ["Visão Geral dos Chamados", "Análise por Bairro", "Impacto de Eventos"]
)

# Função para o dashboard de visão geral dos chamados
def visao_geral_chamados():
  st.title("Visão Geral dos Chamados")
  
  # Seleção de intervalo de datas
  col1, col2 = st.columns(2)
  with col2:
      data_fim = st.date_input("Data Final", datetime.now().date())
  with col1:
      data_inicio = st.date_input("Data Inicial", data_fim - timedelta(days=30))
  
  if data_inicio > data_fim:
      st.error("A data inicial deve ser anterior à data final.")
      return
  
  # Carregar dados
  chamados_df = get_chamados_summary(data_inicio, data_fim)
  
  # Métricas gerais
  total_chamados = chamados_df['contagem'].sum()
  chamados_abertos = chamados_df[chamados_df['status'] == 'ABERTO']['contagem'].sum()
  chamados_fechados = chamados_df[chamados_df['status'] == 'FECHADO']['contagem'].sum()
  
  col1, col2, col3 = st.columns(3)
  col1.metric("Total de Chamados", total_chamados)
  col2.metric("Chamados Abertos", chamados_abertos)
  col3.metric("Chamados Fechados", chamados_fechados)
  
  # Gráfico de chamados por serviço
  chamados_por_servico = chamados_df.groupby('servico')['contagem'].sum().nlargest(10).reset_index()
  
  fig_servico = px.bar(chamados_por_servico, x='servico', y='contagem',
                       title='Top 10 Serviços Solicitados')
  st.plotly_chart(fig_servico)
  
  # Gráfico de evolução temporal dos chamados
  chamados_por_dia = chamados_df.groupby('data')['contagem'].sum().reset_index()
  
  fig_evolucao = px.line(chamados_por_dia, x='data', y='contagem',
                         title='Evolução Diária dos Chamados')
  st.plotly_chart(fig_evolucao)
  
  # Gráfico de pizza para status dos chamados
  status_chamados = chamados_df.groupby('status')['contagem'].sum().reset_index()
  fig_status = px.pie(status_chamados, values='contagem', names='status',
                      title='Distribuição de Status dos Chamados')
  st.plotly_chart(fig_status)

# Função para o dashboard de análise por bairro
def analise_por_bairro():
  st.title("Análise por Bairro")
  
  bairros_df = get_bairros()
  
  # Seletor de bairro
  bairro_selecionado = st.selectbox("Selecione um bairro:", bairros_df['nome'].unique())
  bairro_id = bairros_df[bairros_df['nome'] == bairro_selecionado]['id_bairro'].iloc[0]
  
  chamados_bairro = get_chamados_por_bairro(bairro_id)
  
  # Métricas do bairro
  total_chamados_bairro = len(chamados_bairro)
  chamados_abertos_bairro = chamados_bairro[chamados_bairro['status'] == 'ABERTO'].shape[0]
  
  col1, col2 = st.columns(2)
  col1.metric("Total de Chamados no Bairro", total_chamados_bairro)
  col2.metric("Chamados Abertos no Bairro", chamados_abertos_bairro)
  
  # Gráfico de pizza para tipos de chamados no bairro
  tipos_chamados = chamados_bairro['tipo'].value_counts()
  fig_tipos = px.pie(values=tipos_chamados.values, names=tipos_chamados.index,
                     title=f'Distribuição de Tipos de Chamados em {bairro_selecionado}')
  st.plotly_chart(fig_tipos)
  
  # Mapa de calor dos chamados no bairro
  fig_mapa = px.density_mapbox(chamados_bairro, lat='latitude', lon='longitude', zoom=12,
                               mapbox_style="stamen-terrain",
                               title=f'Mapa de Calor dos Chamados em {bairro_selecionado}')
  st.plotly_chart(fig_mapa)

# Função para o dashboard de impacto de eventos
def impacto_eventos():
  st.title("Impacto de Eventos na Cidade")
  
  eventos_df = get_eventos()
  
  # Seletor de evento
  evento_selecionado = st.selectbox("Selecione um evento:", eventos_df['evento'].unique())
  
  # Filtrando dados para o evento selecionado
  evento_dados = eventos_df[eventos_df['evento'] == evento_selecionado].iloc[0]
  
  # Métricas do evento
  st.metric("Taxa de Ocupação Hoteleira", f"{evento_dados['taxa_ocupacao']:.2f}%")
  
  # Chamados durante o evento
  chamados_evento = get_chamados_por_periodo(evento_dados['data_inicial'], evento_dados['data_final'])
  
  # Gráfico de barras para categorias de chamados durante o evento
  fig_categorias_evento = px.bar(chamados_evento.nlargest(10, 'contagem'), x='categoria', y='contagem',
                                 title=f'Top 10 Categorias de Chamados Durante {evento_selecionado}')
  st.plotly_chart(fig_categorias_evento)
  
  # Comparação de chamados antes, durante e depois do evento
  dias_antes = (evento_dados['data_inicial'] - pd.Timedelta(days=7)).strftime('%Y-%m-%d')
  dias_depois = (evento_dados['data_final'] + pd.Timedelta(days=7)).strftime('%Y-%m-%d')
  
  chamados_antes = get_chamados_por_periodo(dias_antes, evento_dados['data_inicial'])
  chamados_depois = get_chamados_por_periodo(evento_dados['data_final'], dias_depois)
  
  comparacao_df = pd.DataFrame({
      'Período': ['Antes', 'Durante', 'Depois'],
      'Chamados': [chamados_antes['contagem'].sum(), chamados_evento['contagem'].sum(), chamados_depois['contagem'].sum()]
  })
  
  fig_comparacao = px.bar(comparacao_df, x='Período', y='Chamados',
                          title=f'Comparação de Chamados: Antes, Durante e Depois de {evento_selecionado}')
  st.plotly_chart(fig_comparacao)

# Renderizando o dashboard selecionado
if dashboard_selection == "Visão Geral dos Chamados":
  visao_geral_chamados()
elif dashboard_selection == "Análise por Bairro":
  analise_por_bairro()
elif dashboard_selection == "Impacto de Eventos":
  impacto_eventos()