# 💰 Dashboard Financeiro Pessoal

Aplicação interativa desenvolvida com **Streamlit** para análise de finanças pessoais a partir de um arquivo Excel padrão.

O dashboard permite visualizar despesas, receitas, evolução mensal, comparativo com budget e diversos insights financeiros de forma simples e visual.

---

## 🚀 Funcionalidades

* 📊 KPIs principais (Entradas, Saídas, Saldo, Média mensal)
* 📅 Evolução mensal de despesas (por grupo)
* 🏷️ Distribuição por categoria e grupo
* 🌡️ Heatmap (Categoria × Mês)
* 🎯 Comparação de Budget (Real vs Esperado)
* 📉 Fluxo mensal (Receitas × Despesas × Saldo)
* 📋 Tabelas detalhadas de transações
* 🔍 Filtros dinâmicos:

  * Período (mês inicial e final)
  * Grupo
  * Categoria
  * Status (Pago / Pendente)

---

## 🧰 Tecnologias Utilizadas

* Python 3.x
* [Streamlit](https://streamlit.io/)
* Pandas
* Plotly
* OpenPyXL

---

## 📦 Instalação

Clone o repositório e instale as dependências:

```bash
pip install streamlit plotly pandas openpyxl
```

---

## ▶️ Como Executar

No terminal, dentro da pasta do projeto:

```bash
streamlit run dashboard.py
```

O navegador será aberto automaticamente com o dashboard.

---

## 📂 Estrutura do Projeto

```
analise-financeira/
│
├── dashboard.py
├── modelo_dashboard_financeiro.xlsx
├── README.md
```

---

## 📊 Modelo de Dados (Excel)

O dashboard depende de um arquivo `.xlsx` com duas abas principais:

### 🔴 Aba: `DB_DESPESAS`

| Coluna          | Descrição                     |
| --------------- | ----------------------------- |
| Data Lançamento | Data da transação             |
| DESCRIÇÃO       | Descrição da despesa          |
| Entrada(R$)     | Valor de entrada (se houver)  |
| Saída(R$)       | Valor da despesa              |
| CC              | Conta/cartão                  |
| DESC. BASE      | Descrição base                |
| CATEGORIA       | Categoria da despesa          |
| STATUS          | PAGO ou PENDENTE              |
| Data Base       | Data base (mês de referência) |
| GRUPO           | Grupo resumido                |
| GRUPO REAL      | Grupo detalhado               |

---

### 🟢 Aba: `BD_BudgetPessoal`

| Coluna           | Descrição          |
| ---------------- | ------------------ |
| Data Contábil    | Data do lançamento |
| Data Base        | Formato M/YYYY     |
| Título           | Origem da receita  |
| Entrada Real     | Valor recebido     |
| Entrada Esperada | Valor previsto     |

---

## 📌 Como Usar

1. **Baixe o modelo base**

   * Utilize `modelo_dashboard_financeiro.xlsx`

2. **Preencha seus dados**

   * Aba `DB_DESPESAS` → despesas
   * Aba `BD_BudgetPessoal` → receitas/budget

3. **Execute o dashboard**

4. **Faça upload do arquivo**

   * Pela barra lateral do app

5. **Explore os dados**

   * Ajuste filtros e visualize insights

---

## ⚙️ Comportamento do Sistema

* O dashboard inicia com filtro padrão:

  * **Janeiro → Dezembro do ano atual**
* Detecta automaticamente:

  * Aba de despesas (`DESPESAS`)
  * Aba de budget (`BUDGET`)
* Trata automaticamente:

  * Datas inválidas
  * Valores nulos
  * Valores negativos/positivos

---

## 🎨 Personalização

O projeto já possui:

* Tema escuro customizado
* Paleta de cores definida
* Layout otimizado (wide)

Você pode alterar facilmente:

* Cores (dicionário `COLORS`)
* Grupos (`GROUP_LABELS`)
* Layout do dashboard

---

## ⚠️ Possíveis Erros

| Erro                             | Causa                             |
| -------------------------------- | --------------------------------- |
| "Aba de despesas não encontrada" | Nome da aba não contém "DESPESAS" |
| "Aba de budget não encontrada"   | Nome da aba não contém "BUDGET"   |
| Datas vazias                     | Coluna mal preenchida             |
| Valores zerados                  | Dados não numéricos               |

---

## 📈 Melhorias Futuras

* Upload de múltiplos arquivos
* Exportação de relatórios (PDF/Excel)
* Integração com APIs bancárias
* Classificação automática de categorias
* Comparativo entre anos

---

## 👨‍💻 Autor

Projeto desenvolvido para análise financeira pessoal com foco em simplicidade, clareza e tomada de decisão baseada em dados.

---

## 📄 Licença

Uso livre para fins pessoais e educacionais.
