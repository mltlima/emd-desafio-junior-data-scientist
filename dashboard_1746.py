import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import basedosdados as bd
from datetime import datetime, timedelta
import calendar
import requests

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
def get_chamados_por_bairro(bairro_id, data_inicio, data_fim):
  query = f"""
  SELECT 
      tipo,
      status,
      CAST(latitude AS FLOAT64) as latitude,
      CAST(longitude AS FLOAT64) as longitude,
      data_inicio
  FROM `datario.adm_central_atendimento_1746.chamado`
  WHERE id_bairro = '{bairro_id}'
  AND data_inicio BETWEEN '{data_inicio}' AND '{data_fim}'
  AND latitude IS NOT NULL
  AND longitude IS NOT NULL
  """
  return run_query(query)

@st.cache_data(ttl=3600)
def get_chamados_geral(data_inicio, data_fim):
  query = f"""
  SELECT 
      tipo,
      status,
      CAST(latitude AS FLOAT64) as latitude,
      CAST(longitude AS FLOAT64) as longitude,
      data_inicio
  FROM `datario.adm_central_atendimento_1746.chamado`
  WHERE data_inicio BETWEEN '{data_inicio}' AND '{data_fim}'
  AND latitude IS NOT NULL
  AND longitude IS NOT NULL
  """
  return run_query(query)

@st.cache_data(ttl=3600)
def get_eventos():
  query = """
  SELECT *
  FROM `datario.turismo_fluxo_visitantes.rede_hoteleira_ocupacao_eventos`
  """
  return run_query(query)

@st.cache_data(ttl=3600)
def get_chamados_por_periodo(data_inicial, data_final):
  query = f"""
  SELECT 
      tipo,
      COUNT(*) as contagem
  FROM `datario.adm_central_atendimento_1746.chamado`
  WHERE data_inicio BETWEEN '{data_inicial}' AND '{data_final}'
  GROUP BY tipo
  """
  return run_query(query)

@st.cache_data(ttl=3600)
def get_chamados_tendencias(data_inicio, data_fim):
  query = f"""
  SELECT 
      DATE(data_inicio) as data,
      EXTRACT(HOUR FROM data_inicio) as hora,
      EXTRACT(DAYOFWEEK FROM data_inicio) as dia_semana,
      EXTRACT(MONTH FROM data_inicio) as mes,
      tipo,
      COUNT(*) as contagem
  FROM `datario.adm_central_atendimento_1746.chamado`
  WHERE data_inicio BETWEEN '{data_inicio}' AND '{data_fim}'
  GROUP BY data, hora, dia_semana, mes, tipo
  """
  return run_query(query)

@st.cache_data(ttl=3600)
def get_chamados(data_inicio, data_fim):
  query = f"""
  SELECT 
      DATE(data_inicio) as data,
      tipo,
      COUNT(*) as contagem_chamados
  FROM `datario.adm_central_atendimento_1746.chamado`
  WHERE data_inicio BETWEEN '{data_inicio}' AND '{data_fim}'
  GROUP BY data, tipo
  """
  df = run_query(query)
  df['data'] = pd.to_datetime(df['data'])  # Ensure 'data' is datetime
  return df

@st.cache_data(ttl=3600)
def get_weather_data(start_date, end_date):
  latitude = -22.9068
  longitude = -43.1729
  
  url = f"https://archive-api.open-meteo.com/v1/archive?latitude={latitude}&longitude={longitude}&start_date={start_date}&end_date={end_date}&daily=temperature_2m_mean,precipitation_sum&timezone=America%2FSao_Paulo"
  
  response = requests.get(url)
  data = response.json()
  
  df = pd.DataFrame({
      'data': pd.to_datetime(data['daily']['time']),
      'temperatura_media': data['daily']['temperature_2m_mean'],
      'precipitacao': data['daily']['precipitation_sum']
  })
  
  return df


# Sidebar para seleção de dashboard
st.sidebar.title("Navegação")
dashboard_selection = st.sidebar.radio(
  "Escolha um dashboard:",
  ["Visão Geral dos Chamados", "Análise por Bairro", "Mapa Geral de Chamados", 
   "Tendências Temporais", "Impacto Climático", "Impacto de Eventos"]
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
  
  # Seleção de intervalo de datas
  col1, col2 = st.columns(2)
  with col1:
      data_fim = st.date_input("Data Final", datetime.now().date())
  with col2:
      data_inicio = st.date_input("Data Inicial", data_fim - timedelta(days=30))
  
  if data_inicio > data_fim:
      st.error("A data inicial deve ser anterior à data final.")
      return
  
  chamados_bairro = get_chamados_por_bairro(bairro_id, data_inicio, data_fim)
  
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
  
  # Verificar se há dados de latitude e longitude válidos
  valid_coords = chamados_bairro.dropna(subset=['latitude', 'longitude'])
  if len(valid_coords) > 0:
      # Mapa de pins coloridos por tipo de chamado
      fig_mapa = px.scatter_mapbox(valid_coords, 
                                   lat='latitude', 
                                   lon='longitude',
                                   color='tipo',
                                   hover_data=['status', 'data_inicio'],
                                   zoom=11,
                                   mapbox_style="open-street-map",
                                   title=f'Mapa de Chamados em {bairro_selecionado}')
      fig_mapa.update_traces(marker=dict(size=10))
      st.plotly_chart(fig_mapa)
  else:
      st.warning("Não há dados de localização disponíveis para este bairro no período selecionado.")

  # Exibir dados brutos (opcional)
  if st.checkbox("Mostrar dados brutos"):
      st.write(chamados_bairro)

# Função para o dashboard de mapa geral de chamados
def mapa_geral_chamados():
  st.title("Mapa Geral de Chamados")
  
  # Seleção de intervalo de datas
  col1, col2 = st.columns(2)
  with col1:
      data_fim = st.date_input("Data Final", datetime.now().date())
  with col2:
      data_inicio = st.date_input("Data Inicial", data_fim - timedelta(days=30))
  
  if data_inicio > data_fim:
      st.error("A data inicial deve ser anterior à data final.")
      return
  
  chamados_geral = get_chamados_geral(data_inicio, data_fim)
  
  # Métricas gerais
  total_chamados = len(chamados_geral)
  chamados_abertos = chamados_geral[chamados_geral['status'] == 'ABERTO'].shape[0]
  chamados_fechados = chamados_geral[chamados_geral['status'] == 'FECHADO'].shape[0]
  
  col1, col2, col3 = st.columns(3)
  col1.metric("Total de Chamados", total_chamados)
  col2.metric("Chamados Abertos", chamados_abertos)
  col3.metric("Chamados Fechados", chamados_fechados)
  
  # Gráfico de pizza para tipos de chamados
  tipos_chamados = chamados_geral['tipo'].value_counts().nlargest(10)
  fig_tipos = px.pie(values=tipos_chamados.values, names=tipos_chamados.index,
                     title='Top 10 Tipos de Chamados')
  st.plotly_chart(fig_tipos)
  
  # Mapa de pins coloridos por tipo de chamado
  if not chamados_geral.empty:
      fig_mapa = px.scatter_mapbox(chamados_geral, 
                                   lat='latitude', 
                                   lon='longitude',
                                   color='tipo',
                                   hover_data=['status', 'data_inicio'],
                                   zoom=10,
                                   mapbox_style="open-street-map",
                                   title='Mapa Geral de Chamados')
      fig_mapa.update_traces(marker=dict(size=5))  # Reduzimos o tamanho dos marcadores devido à maior quantidade de pontos
      st.plotly_chart(fig_mapa)
  else:
      st.warning("Não há dados de localização disponíveis para o período selecionado.")

  # Exibir dados brutos (opcional)
  if st.checkbox("Mostrar dados brutos"):
      st.write(chamados_geral)


# Função para o dashboard de impacto de eventos
def impacto_eventos():
  st.title("Impacto de Eventos na Cidade")
  
  eventos_df = get_eventos()
  
  # Seletor de evento
  evento_selecionado = st.selectbox("Selecione um evento:", eventos_df['evento'].unique())
  
  # Filtrando dados para o evento selecionado
  evento_dados = eventos_df[eventos_df['evento'] == evento_selecionado].iloc[0]
  
  # Métricas do evento
  st.metric("Taxa de Ocupação Hoteleira", f"{100 * evento_dados['taxa_ocupacao']:.2f}%")
  
  # Chamados durante o evento
  chamados_evento = get_chamados_por_periodo(evento_dados['data_inicial'], evento_dados['data_final'])
  
  # Gráfico de barras para categorias de chamados durante o evento
  fig_categorias_evento = px.bar(chamados_evento.nlargest(10, 'contagem'), x='tipo', y='contagem',
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

# Dashboard de tendências temporais
def dashboard_tendencias_temporais():
  st.title("Dashboard de Tendências Temporais")
  
  # Seleção de intervalo de datas
  col1, col2 = st.columns(2)
  with col1:
      data_fim = st.date_input("Data Final", datetime.now().date())
  with col2:
      data_inicio = st.date_input("Data Inicial", data_fim - timedelta(days=180))  # Padrão para 6 meses
  
  if data_inicio > data_fim:
      st.error("A data inicial deve ser anterior à data final.")
      return
  
  chamados_tendencias = get_chamados_tendencias(data_inicio, data_fim)
  
  # 1. Gráfico de linha mostrando a evolução dos chamados ao longo do tempo
  chamados_diarios = chamados_tendencias.groupby('data')['contagem'].sum().reset_index()
  fig_evolucao = px.line(chamados_diarios, x='data', y='contagem',
                         title='Evolução Diária dos Chamados')
  st.plotly_chart(fig_evolucao)
  
  # 2. Heatmap dos chamados por hora do dia e dia da semana
  heatmap_data = chamados_tendencias.groupby(['dia_semana', 'hora'])['contagem'].sum().reset_index()
  heatmap_data = heatmap_data.pivot(index='dia_semana', columns='hora', values='contagem')
  
  dias_semana = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']
  heatmap_data.index = dias_semana
  
  fig_heatmap = go.Figure(data=go.Heatmap(
                 z=heatmap_data.values,
                 x=heatmap_data.columns,
                 y=heatmap_data.index,
                 colorscale='Viridis'))
  
  fig_heatmap.update_layout(
      title='Heatmap de Chamados por Hora e Dia da Semana',
      xaxis_title='Hora do Dia',
      yaxis_title='Dia da Semana'
  )
  st.plotly_chart(fig_heatmap)
  
  # 3. Análise mensal dos tipos de chamados
  chamados_mensais = chamados_tendencias.groupby(['mes', 'tipo'])['contagem'].sum().reset_index()
  top_tipos = chamados_mensais.groupby('tipo')['contagem'].sum().nlargest(5).index
  chamados_mensais_top = chamados_mensais[chamados_mensais['tipo'].isin(top_tipos)]
  
  chamados_mensais_top['mes'] = chamados_mensais_top['mes'].apply(lambda x: calendar.month_abbr[x])
  
  fig_mensal = px.line(chamados_mensais_top, x='mes', y='contagem', color='tipo',
                       title='Tendência Mensal dos Top 5 Tipos de Chamados')
  fig_mensal.update_xaxes(categoryorder='array', categoryarray=list(calendar.month_abbr)[1:])
  st.plotly_chart(fig_mensal)
  
  # 4. Distribuição dos tipos de chamados
  tipos_chamados = chamados_tendencias.groupby('tipo')['contagem'].sum().nlargest(10).reset_index()
  fig_tipos = px.pie(tipos_chamados, values='contagem', names='tipo',
                     title='Top 10 Tipos de Chamados')
  st.plotly_chart(fig_tipos)


def dashboard_impacto_climatico():
  st.title("Dashboard de Impacto Climático")
  
  col1, col2 = st.columns(2)
  with col1:
      data_fim = st.date_input("Data Final", datetime.now().date())
  with col2:
      data_inicio = st.date_input("Data Inicial", data_fim - timedelta(days=30))
  
  if data_inicio > data_fim:
      st.error("A data inicial deve ser anterior à data final.")
      return
  
  chamados = get_chamados(data_inicio, data_fim)
  clima = get_weather_data(data_inicio, data_fim)
  
  chamados_clima = pd.merge(chamados, clima, on='data')
  chamados_diarios = chamados_clima.groupby('data').agg({
    'contagem_chamados': 'sum',
    'temperatura_media': 'mean',
    'precipitacao': 'mean'
  }).reset_index()
  
  fig_temp = go.Figure()
  fig_temp.add_trace(go.Scatter(x=chamados_diarios['data'], y=chamados_diarios['contagem_chamados'],
                                name='Chamados', yaxis='y1'))
  fig_temp.add_trace(go.Scatter(x=chamados_diarios['data'], y=chamados_diarios['temperatura_media'],
                                name='Temperatura Média', yaxis='y2'))

  fig_temp.update_layout(
    title='Relação entre Chamados e Temperatura',
    xaxis_title='Data',
    yaxis_title='Número de Chamados',
    yaxis2=dict(
        title='Temperatura Média (°C)',
        overlaying='y',
        side='right'
    )
  )
  st.plotly_chart(fig_temp)
  
  # Gráfico de Chamados vs. Precipitação
  dias_com_chuva = chamados_diarios[chamados_diarios['precipitacao'] > 0]
  fig_precip = go.Figure()
  fig_precip.add_trace(go.Scatter(
      x=dias_com_chuva['precipitacao'],
      y=dias_com_chuva['contagem_chamados'],
      mode='markers',
      marker=dict(
          size=dias_com_chuva['contagem_chamados'] / 10,
          sizemode='area',
          sizeref=2.*max(dias_com_chuva['contagem_chamados'])/(40.**2),
          sizemin=4
      ),
      text=dias_com_chuva['data'],
      hovertemplate='Data: %{text}<br>Precipitação: %{x:.1f}mm<br>Chamados: %{y}<extra></extra>'
  ))
  fig_precip.update_layout(
      title='Relação entre Chamados e Precipitação (Dias com Chuva)',
      xaxis_title='Precipitação (mm)',
      yaxis_title='Número de Chamados'
  )
  st.plotly_chart(fig_precip)
  
  # Categorização da precipitação
  def categorizar_precipitacao(valor):
      if valor == 0:
          return 'Sem chuva'
      elif valor <= 5:
          return 'Chuva leve'
      elif valor <= 25:
          return 'Chuva moderada'
      else:
          return 'Chuva forte'

  chamados_diarios['categoria_precipitacao'] = chamados_diarios['precipitacao'].apply(categorizar_precipitacao)
  media_por_categoria = chamados_diarios.groupby('categoria_precipitacao')['contagem_chamados'].mean().reset_index()

  fig_categoria = px.bar(media_por_categoria, x='categoria_precipitacao', y='contagem_chamados',
                         title='Média de Chamados por Categoria de Precipitação')
  st.plotly_chart(fig_categoria)
  
  # Create the heatmap
  chamados_temp = chamados_clima.groupby(['tipo', pd.cut(chamados_clima['temperatura_media'], bins=5)])['contagem_chamados'].mean().unstack()
  chamados_temp.columns = chamados_temp.columns.astype(str)
  chamados_temp = chamados_temp.fillna(0)

  fig_heatmap = px.imshow(
      chamados_temp,
      labels=dict(x="Faixa de Temperatura", y="Tipo de Chamado", color="Média de Chamados"),
      title="Heatmap: Tipos de Chamados vs. Temperatura"
  )
  
  # Display the heatmap
  st.plotly_chart(fig_heatmap)
  
  dias_chuvosos = chamados_clima[chamados_clima['precipitacao'] > 10]
  top_tipos_chuva = dias_chuvosos.groupby('tipo')['contagem_chamados'].sum().nlargest(5).reset_index()
  
  fig_top_chuva = px.bar(top_tipos_chuva, x='tipo', y='contagem_chamados',
                         title='Top 5 Tipos de Chamados em Dias Chuvosos')
  st.plotly_chart(fig_top_chuva)

# Renderizando o dashboard selecionado
if dashboard_selection == "Visão Geral dos Chamados":
  visao_geral_chamados()
elif dashboard_selection == "Análise por Bairro":
  analise_por_bairro()
elif dashboard_selection == "Mapa Geral de Chamados":
  mapa_geral_chamados()
elif dashboard_selection == "Tendências Temporais":
  dashboard_tendencias_temporais()
elif dashboard_selection == "Impacto Climático":
  dashboard_impacto_climatico()
elif dashboard_selection == "Impacto de Eventos":
  impacto_eventos()