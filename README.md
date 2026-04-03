# 💰 Dashboard Financeiro Pessoal

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?style=flat-square&logo=streamlit)
![Plotly](https://img.shields.io/badge/Plotly-5.x-3F4F75?style=flat-square&logo=plotly)
![License](https://img.shields.io/badge/Licença-Pessoal%2FEducacional-green?style=flat-square)

Aplicação interativa desenvolvida com Streamlit para análise de finanças pessoais a partir de um arquivo Excel padrão.

O dashboard permite visualizar despesas, receitas, evolução mensal, comparativo com budget e diversos insights financeiros de forma simples e visual. Ao ser iniciado sem dados, exibe uma tela de boas-vindas com instruções de uso — basta fazer o upload do Excel pela barra lateral para o dashboard carregar imediatamente.

---

## 🚀 Funcionalidades

- 📊 **KPIs principais** — Entradas, Saídas, Saldo líquido e Média mensal
- 📅 **Evolução mensal de despesas** por grupo (gráfico de barras empilhadas)
- 🏷️ **Distribuição por categoria e grupo** (ranking horizontal + pizza)
- 🌡️ **Heatmap** Categoria × Mês
- 🎯 **Comparação de Budget** — Real vs Esperado com gauge de % realizado
- 📉 **Fluxo mensal** — Receitas × Despesas × Saldo
- 📋 **Tabelas detalhadas** de transações e budget
- 🔍 **Filtros dinâmicos:** período, grupo, categoria e status (Pago / Pendente)
- 👋 **Estado zero** — tela de boas-vindas com guia de uso quando nenhum arquivo está carregado

---

## 🧰 Tecnologias Utilizadas

| Biblioteca | Uso |
|------------|-----|
| [Streamlit](https://streamlit.io) | Interface web e componentes interativos |
| [Pandas](https://pandas.pydata.org) | Leitura e manipulação dos dados |
| [Plotly](https://plotly.com/python) | Gráficos interativos |
| [OpenPyXL](https://openpyxl.readthedocs.io) | Leitura e criação de arquivos Excel |

---

## 📦 Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/dashboard-financeiro.git
cd dashboard-financeiro

# 2. (Opcional) Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt
```

> **requirements.txt**
> ```
> streamlit
> plotly
> pandas
> openpyxl
> ```

---

## ▶️ Como Executar

```bash
streamlit run dashboard.py
```

O navegador será aberto automaticamente. Se não abrir, acesse `http://localhost:8501`.

---

## 📂 Estrutura do Projeto

```
dashboard-financeiro/
│
├── dashboard.py                      # Aplicação principal
├── modelo_dashboard_financeiro.xlsx  # Modelo de dados para preenchimento
├── requirements.txt                  # Dependências do projeto
└── README.md
```

---

## 📊 Modelo de Dados (Excel)

O dashboard detecta automaticamente as abas por nome (busca por `DESPESAS` e `BUDGET`). Use o arquivo `modelo_dashboard_financeiro.xlsx` como base — ele já contém exemplos preenchidos, validações de dados e uma aba de instruções.

### 🔴 Aba: DB_DESPESAS

| Coluna | Descrição |
|--------|-----------|
| `Data Lançamento` | Data real da transação (dd/mm/aaaa) |
| `DESCRIÇÃO` | Descrição da despesa |
| `Entrada(R$)` | Valor de entrada — use `0` se for saída |
| `Saída(R$)` | Valor da despesa — use `0` se for entrada |
| `CC` | Conta ou cartão de origem (ex: NUBANK, C6) |
| `DESC. BASE` | Descrição resumida da categoria |
| `CATEGORIA` | Categoria detalhada (ex: D.P. Alimentação) |
| `STATUS` | `PAGO` ou `PENDENTE` |
| `Data Base` | Mês de competência — dia sempre `01` (ex: 01/01/2027) |
| `GRUPO` | Grupo resumido: `D.P.` · `D.T.` · `D.F.` · `PGT.` · `Vend` |
| `GRUPO REAL` | Igual ao GRUPO na maioria dos casos |

### 🟢 Aba: BD_BudgetPessoal

| Coluna | Descrição |
|--------|-----------|
| `Data Contábil` | Data do recebimento (dd/mm/aaaa) |
| `Data Base` | Período no formato `M/AAAA` (ex: `3/2027`) |
| `Título` | Origem da receita (ex: SALÁRIO, FREELANCE, 13° 1/2) |
| `Entrada Real` | Valor efetivamente recebido — deixe em branco se ainda não recebeu |
| `Entrada Esperada` | Valor previsto/planejado |

---

## 📌 Como Usar

1. **Baixe o modelo base**
   - Utilize `modelo_dashboard_financeiro.xlsx` como ponto de partida

2. **Preencha seus dados**
   - `DB_DESPESAS` → suas transações e despesas
   - `BD_BudgetPessoal` → receitas realizadas e previstas

3. **Execute o dashboard**
   ```bash
   streamlit run dashboard.py
   ```

4. **Faça o upload do arquivo**
   - Clique em *"Faça upload do seu Excel"* na barra lateral

5. **Explore os dados**
   - Ajuste os filtros de período, grupo, categoria e status

---

## ⚙️ Comportamento do Sistema

- **Filtro padrão ao carregar:** Janeiro → Dezembro do **ano atual** (detectado automaticamente pela data do servidor)
- **Detecção automática de abas:** busca por substring — `DESPESAS` e `BUDGET` — sem necessidade de nome exato
- **Tratamento automático de dados:** datas inválidas, valores nulos, e valores negativos são normalizados na leitura

---

## ⚠️ Possíveis Erros

| Erro | Causa | Solução |
|------|-------|---------|
| `"Aba de despesas não encontrada"` | Nome da aba não contém `DESPESAS` | Renomeie para `DB_DESPESAS` ou `BD_DESPESAS` |
| `"Aba de budget não encontrada"` | Nome da aba não contém `BUDGET` | Renomeie para `BD_BudgetPessoal` |
| Datas exibidas como `NaT` | Coluna de data mal preenchida ou formato incorreto | Use o formato `dd/mm/aaaa` |
| Valores zerados nos gráficos | Dados não numéricos nas colunas de valor | Verifique se não há texto ou células mescladas |

---

## 🎨 Personalização

O projeto foi desenvolvido com tema escuro e paleta de cores própria. Os principais pontos de customização estão no topo do `dashboard.py`:

```python
# Cores dos componentes
COLORS = { "primary": "#7c83ff", "success": "#4caf7d", ... }

# Paleta dos gráficos
CAT_PALETTE = ["#7c83ff", "#4caf7d", "#f05454", ...]

# Rótulos dos grupos
GROUP_LABELS = { "D.P.": "Despesas Pessoais", "D.T.": "Transporte/Fixas", ... }
```

---

## 📈 Melhorias Futuras

- [ ] Upload de múltiplos arquivos para comparativo entre períodos
- [ ] Exportação de relatórios em PDF ou Excel
- [ ] Integração com APIs bancárias (Open Finance)
- [ ] Classificação automática de categorias com IA
- [ ] Comparativo entre anos no mesmo painel

---

## 👨‍💻 Autor

Desenvolvido por **[Patrick Coelho]** — [GitHub](https://github.com/coelhp) · [Linkedin](https://linkedin.com/in/patrick-riquelme-santos-coelho-845b82230/)

Projeto criado para análise financeira pessoal com foco em simplicidade, clareza e tomada de decisão baseada em dados.

---

## 📄 Licença

Uso livre para fins pessoais e educacionais.
