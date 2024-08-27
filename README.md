# Desafio Técnico - Cientista de Dados Júnior

Este repositório contém um conjunto de dashboards interativos que analisam dados de chamados, condições climáticas e feriados. Os dashboards são construídos usando Streamlit e Plotly.
    
As repostas das questões estão em sql e em python estão em um Jupyter Notebook para melhor visualização


## Configuração do Ambiente

1. **Clone o repositório:**

    ```bash
    git clone git@github.com:mltlima/emd-desafio-junior-data-scientist.git
    cd dashboard_1746
2. **Crie um arquivo `.env`:**

   Crie um arquivo chamado `.env` no diretório do projeto e adicione suas variáveis de ambiente, ou somente remove o `.example` já presente diretório

        billing_project_id


3. **Instale as dependências:**

    ```bash
    pip install -r requirements.txt
## Executando o Dashboard

### Usando Streamlit

1. **Executar dashboard:**

```bash
streamlit run dashboard_1746.py
```
ou
```bash
python -m streamlit run dashboard_1746.py
```

2. **Acesse o Dashboard:**

   Abra seu navegador e vá para `http://localhost:8501`.

## Executando Análises SQL

1. **Resposta salvas em um arquivo `analise_sql.sql`. Rodar usando o BigQuery.**

## Executando Análises em Python

1. **Para acessar os dados do BigQuery no Python, siga o tutorial acima e utilize a biblioteca `basedosdados` depois dados podem ser rodados por células pelo `analise_python.ipynb`.**

## Executando Análises de API

1. **Novamente acessar os dados do BigQuery no Python e rodar as células `analise_api.ipynb`.**
