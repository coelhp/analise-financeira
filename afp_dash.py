"""
Dashboard Financeiro Pessoal — v0
Análise das guias DB_DESPESAS e BD_BudgetPessoal

Requisitos:
    pip install streamlit plotly pandas openpyxl

Execução:
    streamlit run afp_dash.py

Ao inicializar sem arquivo, o dashboard exibe uma tela de boas-vindas com
instruções de upload. O filtro de período já vem pré-configurado para
Janeiro → Dezembro do ANO ATUAL (baseado na data do servidor).
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import date
from pathlib import Path
import tempfile, shutil

# ─── Configuração da Página ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard de Análise Financeira Pessoal",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS Customizado ───────────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #141726; }
    .section-title {
        font-size: 17px; font-weight: 600; color: #7c83ff;
        margin: 22px 0 10px; border-bottom: 1px solid #2d3250; padding-bottom: 6px;
    }
    .empty-state {
        text-align: center; padding: 60px 20px;
        border: 2px dashed #2d3250; border-radius: 16px;
        margin: 40px auto; max-width: 700px;
    }
    .empty-state h2 { color: #7c83ff; margin-bottom: 10px; }
    .empty-state p  { color: #a0aab4; font-size: 15px; }
    .step-box {
        background: #1e2130; border-radius: 12px;
        padding: 18px 24px; margin: 10px 0; border-left: 4px solid #7c83ff;
    }
    .step-box b { color: #7c83ff; }
</style>
""", unsafe_allow_html=True)

# ─── Paleta ───────────────────────────────────────────────────────────────────
COLORS = {
    "primary":   "#7c83ff",
    "success":   "#4caf7d",
    "danger":    "#f05454",
    "warning":   "#f5a623",
    "secondary": "#a0aab4",
    "bg":        "#1e2130",
    "grid":      "#2d3250",
}
CAT_PALETTE = [
    "#7c83ff","#4caf7d","#f05454","#f5a623","#56cfe1",
    "#ff7096","#c77dff","#06d6a0","#ff9f1c","#2ec4b6",
    "#e76f51","#457b9d","#a8dadc","#ffd166","#ef476f",
    "#118ab2","#06d6a0","#ffd166","#ef476f","#073b4c",
]
GROUP_LABELS = {
    "D.P.": "Despesas Pessoais",
    "D.T.": "Transporte/Fixas",
    "D.F.": "Financeiras",
    "PGT.": "Pagamentos",
    "Vend": "Vendas/Receitas",
}

# ─── Ano atual (base para filtros padrão) ─────────────────────────────────────
CURRENT_YEAR  = date.today().year
DEFAULT_START = f"{CURRENT_YEAR}-01"   # formato YYYY-MM (Period string)
DEFAULT_END   = f"{CURRENT_YEAR}-12"

# ─── Carregamento de Dados ─────────────────────────────────────────────────────
@st.cache_data
def load_data(filepath: str):
    xl = pd.ExcelFile(filepath)

    # Localiza aba de despesas (aceita DB_ ou BD_)
    desp_candidates = [s for s in xl.sheet_names if "DESPESAS" in s.upper()]
    if not desp_candidates:
        raise ValueError("Aba de despesas não encontrada. Certifique-se de ter uma aba com 'DESPESAS' no nome.")
    df = pd.read_excel(xl, sheet_name=desp_candidates[0], header=0)
    df.columns = df.columns.str.strip()

    df["Data Lançamento"] = pd.to_datetime(df["Data Lançamento"], errors="coerce")
    df["Data Base"]       = pd.to_datetime(df["Data Base"],       errors="coerce")
    df["Saída(R$)"]       = pd.to_numeric(df["Saída(R$)"],  errors="coerce").abs().fillna(0)
    df["Entrada(R$)"]     = pd.to_numeric(df["Entrada(R$)"],errors="coerce").abs().fillna(0)
    df["AnoMes"]          = df["Data Base"].dt.to_period("M").astype(str)

    group_col = "GRUPO REAL" if "GRUPO REAL" in df.columns else "GRUPO"
    df["GRUPO LABEL"] = df[group_col].map(GROUP_LABELS).fillna(df[group_col])

    # Localiza aba de budget
    bud_candidates = [s for s in xl.sheet_names if "BUDGET" in s.upper()]
    if not bud_candidates:
        raise ValueError("Aba de budget não encontrada. Certifique-se de ter uma aba com 'BUDGET' no nome.")
    bdf = pd.read_excel(xl, sheet_name=bud_candidates[0], header=0)
    bdf.columns = bdf.columns.str.strip()
    bdf["Data Contábil"]    = pd.to_datetime(bdf["Data Contábil"], errors="coerce")
    bdf["Entrada Real"]     = pd.to_numeric(bdf["Entrada Real"],     errors="coerce").fillna(0)
    bdf["Entrada Esperada"] = pd.to_numeric(bdf["Entrada Esperada"], errors="coerce").fillna(0)

    def parse_period(val):
        try:
            parts = str(val).split("/")
            m, y = int(parts[0]), int(parts[1])
            return pd.Period(year=y, month=m, freq="M").strftime("%Y-%m")
        except Exception:
            return None

    bdf["AnoMes"] = bdf["Data Base"].apply(parse_period)
    return df, bdf, group_col


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — Upload + Filtros
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 📂 Upload do Arquivo de Dados")
    uploaded = st.file_uploader(
        "Faça upload do seu Excel (.xlsx)",
        type=["xlsx"],
        help="Use o modelo_dashboard_financeiro.xlsx como ponto de partida.",
    )

    filepath   = None
    df         = None
    bdf        = None
    group_col  = "GRUPO REAL"
    load_error = None

    default_file = Path(__file__).parent / "CC_-_PT_v3_1.xlsx"

    if uploaded:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        shutil.copyfileobj(uploaded, tmp)
        tmp.flush()
        filepath = tmp.name
    elif default_file.exists():
        filepath = str(default_file)

    if filepath:
        try:
            df, bdf, group_col = load_data(filepath)
        except Exception as e:
            load_error = str(e)

    # Filtros (só exibe com dados)
    if df is not None:
        st.markdown("---")
        st.markdown("## 🔍 Filtros")

        all_months = sorted(df["AnoMes"].dropna().unique())

        def pick_idx(months, target, fallback):
            return months.index(target) if target in months else fallback

        idx_start = pick_idx(all_months, DEFAULT_START, 0)
        idx_end   = pick_idx(all_months, DEFAULT_END,   len(all_months) - 1)

        col1, col2 = st.columns(2)
        with col1:
            start_m = st.selectbox("De",  all_months, index=idx_start, key="start_m")
        with col2:
            end_m   = st.selectbox("Até", all_months, index=idx_end,   key="end_m")

        valid_range = [m for m in all_months if start_m <= m <= end_m]

        all_groups = sorted(df[group_col].dropna().unique())
        sel_groups = st.multiselect("Grupos", all_groups, default=all_groups)

        all_cats   = sorted(df["CATEGORIA"].dropna().unique())
        sel_cats   = st.multiselect("Categorias", all_cats, default=all_cats)

        status_opts = sorted(df["STATUS"].dropna().unique())
        sel_status  = st.multiselect("Status", status_opts, default=status_opts)

        st.markdown("---")
        st.caption(f"📅 Filtro padrão: ano atual **{CURRENT_YEAR}**")


# ══════════════════════════════════════════════════════════════════════════════
# ESTADO ZERO — sem arquivo carregado
# ══════════════════════════════════════════════════════════════════════════════
if df is None:
    st.title("💰 Dashboard de Finanças Pessoais")

    if load_error:
        st.error(f"❌ Erro ao carregar o arquivo: {load_error}")
    else:
        st.markdown("""
        <div class="empty-state">
            <h2>Bem-vindo ao Dashboard! 👋</h2>
            <p>Nenhum dado carregado ainda.<br>
            Faça o upload do seu arquivo Excel na barra lateral para começar.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">📋 Como usar</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="step-box">
            <b>① Baixe o modelo</b><br>
            Use o arquivo <code>modelo_dashboard_financeiro.xlsx</code>
            como base — ele já contém as abas e exemplos prontos.
        </div>
        <div class="step-box">
            <b>② Preencha os dados</b><br>
            Insira suas transações na aba <code>DB_DESPESAS</code>
            e suas receitas em <code>BD_BudgetPessoal</code>.
            Consulte a aba <code>INSTRUÇÕES</code> para detalhes de cada coluna.
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="step-box">
            <b>③ Faça o upload</b><br>
            Clique em <i>"Faça upload do seu Excel"</i> na barra lateral
            e selecione seu arquivo preenchido.
        </div>
        <div class="step-box">
            <b>④ Explore os dados</b><br>
            O dashboard já inicia com o filtro de
            <b>Janeiro a Dezembro de {CURRENT_YEAR}</b>.
            Use a barra lateral para ajustar período, grupos e categorias.
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">📐 Estrutura esperada do Excel</div>', unsafe_allow_html=True)

    tab_desp, tab_bud = st.tabs(["🔴 DB_DESPESAS", "🟢 BD_BudgetPessoal"])
    with tab_desp:
        st.dataframe(pd.DataFrame({
            "Data Lançamento": ["05/01/2027", "08/01/2027"],
            "DESCRIÇÃO":        ["SUPERMERCADO EXEMPLO", "POSTO COMBUSTIVEL"],
            "Entrada(R$)":      [0, 0],
            "Saída(R$)":        [-250.00, -180.00],
            "CC":               ["NUBANK", "C6"],
            "DESC. BASE":       ["SUPERMERCADO", "ABASTECIMENTO"],
            "CATEGORIA":        ["D.P. Alimentação", "D.T. Combustível"],
            "STATUS":           ["PAGO", "PAGO"],
            "Data Base":        ["01/01/2027", "01/01/2027"],
            "GRUPO":            ["D.P.", "D.T."],
            "GRUPO REAL":       ["D.P.", "D.T."],
        }), use_container_width=True)
    with tab_bud:
        st.dataframe(pd.DataFrame({
            "Data Contábil":    ["05/01/2027", "05/02/2027"],
            "Data Base":        ["1/2027", "2/2027"],
            "Título":           ["SALÁRIO", "SALÁRIO"],
            "Entrada Real":     [5800.00, 5800.00],
            "Entrada Esperada": [5800.00, 5800.00],
        }), use_container_width=True)

    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# DADOS CARREGADOS — dashboard completo
# ══════════════════════════════════════════════════════════════════════════════

mask = (
    df["AnoMes"].isin(valid_range) &
    df[group_col].isin(sel_groups) &
    df["CATEGORIA"].isin(sel_cats) &
    df["STATUS"].isin(sel_status)
)
fdf       = df[mask].copy()
bdf_range = bdf[bdf["AnoMes"].isin(valid_range)].copy()

# Header
st.title("💰 Dashboard de Finanças Pessoais")
st.caption(
    f"Período: **{start_m}** → **{end_m}** · "
    f"{len(valid_range)} meses · {len(fdf):,} transações"
)

# ── KPIs ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📊 Resumo do Período</div>', unsafe_allow_html=True)

total_saida    = fdf["Saída(R$)"].sum()
total_entrada  = fdf["Entrada(R$)"].sum()
saldo          = total_entrada - total_saida
pago           = fdf[fdf["STATUS"] == "PAGO"]["Saída(R$)"].sum()
pendente       = fdf[fdf["STATUS"] == "PENDENTE"]["Saída(R$)"].sum()
media_mensal   = fdf.groupby("AnoMes")["Saída(R$)"].sum().mean() if valid_range else 0
total_real     = bdf_range["Entrada Real"].sum()
total_esperado = bdf_range["Entrada Esperada"].sum()
budget_gap     = total_real - total_esperado

k1,k2,k3,k4,k5,k6 = st.columns(6)
k1.metric("💸 Total Saídas",   f"R$ {total_saida:,.0f}")
k2.metric("💵 Total Entradas", f"R$ {total_entrada:,.0f}")
k3.metric("📈 Saldo Líquido",  f"R$ {saldo:,.0f}",    delta=f"R$ {saldo:,.0f}")
k4.metric("✅ Pago",           f"R$ {pago:,.0f}")
k5.metric("⏳ Pendente",       f"R$ {pendente:,.0f}", delta_color="inverse")
k6.metric("📅 Média Mensal",   f"R$ {media_mensal:,.0f}")

# ── Evolução Mensal ───────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📅 Evolução Mensal de Despesas</div>', unsafe_allow_html=True)

monthly_grp = (
    fdf.groupby(["AnoMes", group_col, "GRUPO LABEL"])["Saída(R$)"]
    .sum().reset_index().sort_values("AnoMes")
)
if not monthly_grp.empty:
    fig_evo = px.bar(
        monthly_grp, x="AnoMes", y="Saída(R$)", color="GRUPO LABEL",
        color_discrete_sequence=CAT_PALETTE,
        labels={"AnoMes":"Mês","Saída(R$)":"R$","GRUPO LABEL":"Grupo"},
        template="plotly_dark",
    )
    fig_evo.update_layout(
        plot_bgcolor=COLORS["bg"], paper_bgcolor=COLORS["bg"],
        legend=dict(orientation="h", y=-0.22),
        xaxis=dict(tickangle=-45), barmode="stack",
        margin=dict(t=10, b=70),
    )
    st.plotly_chart(fig_evo, use_container_width=True)
else:
    st.info("Nenhuma despesa no período selecionado.")

# ── Por Categoria + Grupos ────────────────────────────────────────────────────
st.markdown('<div class="section-title">🏷️ Distribuição por Categoria e Grupo</div>', unsafe_allow_html=True)

col_a, col_b = st.columns([1.3, 1])
with col_a:
    cat_sum = fdf.groupby("CATEGORIA")["Saída(R$)"].sum().sort_values(ascending=True).reset_index()
    if not cat_sum.empty:
        fig_cat = px.bar(
            cat_sum, x="Saída(R$)", y="CATEGORIA", orientation="h",
            color="Saída(R$)", color_continuous_scale="Blues",
            labels={"Saída(R$)":"R$","CATEGORIA":""}, template="plotly_dark",
        )
        fig_cat.update_layout(
            plot_bgcolor=COLORS["bg"], paper_bgcolor=COLORS["bg"],
            coloraxis_showscale=False, margin=dict(t=10,b=10,l=10,r=10), height=460,
        )
        st.plotly_chart(fig_cat, use_container_width=True)
    else:
        st.info("Sem dados de categoria no período.")

with col_b:
    grp_sum = fdf.groupby("GRUPO LABEL")["Saída(R$)"].sum().reset_index()
    if not grp_sum.empty:
        fig_pie = px.pie(
            grp_sum, values="Saída(R$)", names="GRUPO LABEL",
            color_discrete_sequence=CAT_PALETTE,
            template="plotly_dark", hole=0.45,
        )
        fig_pie.update_traces(textposition="outside", textinfo="percent+label")
        fig_pie.update_layout(
            plot_bgcolor=COLORS["bg"], paper_bgcolor=COLORS["bg"],
            showlegend=False, margin=dict(t=10,b=10,l=10,r=10), height=460,
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Sem dados de grupo no período.")

# ── Heatmap ───────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🌡️ Heatmap: Categoria × Mês</div>', unsafe_allow_html=True)

if not fdf.empty:
    heat = (
        fdf.groupby(["AnoMes","CATEGORIA"])["Saída(R$)"]
        .sum().unstack(fill_value=0).sort_index()
    )
    heat = heat[sorted(heat.columns)]
    fig_heat = go.Figure(data=go.Heatmap(
        z=heat.values, x=heat.columns.tolist(), y=heat.index.tolist(),
        colorscale="Blues",
        text=[[f"R$ {v:,.0f}" for v in row] for row in heat.values],
        texttemplate="%{text}", textfont={"size": 9}, hoverongaps=False,
    ))
    fig_heat.update_layout(
        plot_bgcolor=COLORS["bg"], paper_bgcolor=COLORS["bg"],
        margin=dict(t=10,b=10), height=420,
        xaxis=dict(tickangle=-45), font=dict(color="#e8eaf0"),
    )
    st.plotly_chart(fig_heat, use_container_width=True)
else:
    st.info("Sem dados para o heatmap no período selecionado.")

# ── Budget Pessoal ────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🎯 Budget Pessoal — Entradas Real vs Esperado</div>', unsafe_allow_html=True)

bk1, bk2, bk3 = st.columns(3)
bk1.metric("💰 Entrada Real",         f"R$ {total_real:,.0f}")
bk2.metric("🎯 Entrada Esperada",     f"R$ {total_esperado:,.0f}")
bk3.metric("📊 Gap Real vs Esperado", f"R$ {budget_gap:,.0f}", delta=f"R$ {budget_gap:,.0f}")

bud_monthly = (
    bdf_range.groupby("AnoMes")[["Entrada Real","Entrada Esperada"]]
    .sum().reset_index().sort_values("AnoMes")
)

if not bud_monthly.empty:
    fig_bud = go.Figure()
    fig_bud.add_trace(go.Bar(
        x=bud_monthly["AnoMes"], y=bud_monthly["Entrada Esperada"],
        name="Esperado", marker_color=COLORS["secondary"], opacity=0.6,
    ))
    fig_bud.add_trace(go.Bar(
        x=bud_monthly["AnoMes"], y=bud_monthly["Entrada Real"],
        name="Real", marker_color=COLORS["success"],
    ))
    fig_bud.update_layout(
        barmode="group",
        plot_bgcolor=COLORS["bg"], paper_bgcolor=COLORS["bg"],
        legend=dict(orientation="h", y=-0.22),
        xaxis=dict(tickangle=-45), yaxis_title="R$",
        margin=dict(t=10,b=70), font=dict(color="#e8eaf0"), template="plotly_dark",
    )
    st.plotly_chart(fig_bud, use_container_width=True)

    col_c, col_d = st.columns([1, 1])
    with col_c:
        bud_titulo = (
            bdf_range.groupby("Título")[["Entrada Real","Entrada Esperada"]]
            .sum().sort_values("Entrada Real", ascending=False).reset_index()
        )
        fig_titulo = go.Figure()
        fig_titulo.add_trace(go.Bar(
            x=bud_titulo["Título"], y=bud_titulo["Entrada Esperada"],
            name="Esperado", marker_color=COLORS["secondary"], opacity=0.6,
        ))
        fig_titulo.add_trace(go.Bar(
            x=bud_titulo["Título"], y=bud_titulo["Entrada Real"],
            name="Real", marker_color=COLORS["success"],
        ))
        fig_titulo.update_layout(
            barmode="group", title="Entradas por Título",
            plot_bgcolor=COLORS["bg"], paper_bgcolor=COLORS["bg"],
            xaxis=dict(tickangle=-35), legend=dict(orientation="h", y=-0.3),
            margin=dict(t=40,b=80), height=380,
            font=dict(color="#e8eaf0"), template="plotly_dark",
        )
        st.plotly_chart(fig_titulo, use_container_width=True)

    with col_d:
        pct = (total_real / total_esperado * 100) if total_esperado > 0 else 0
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=pct,
            number={"suffix":"%","font":{"color":"#e8eaf0"}},
            delta={"reference":100,"suffix":"%"},
            title={"text":"% do Budget Realizado","font":{"color":"#e8eaf0","size":15}},
            gauge={
                "axis":{"range":[0,120],"tickcolor":"#a0aab4"},
                "bar":{"color":COLORS["primary"]},
                "steps":[
                    {"range":[0,70],   "color":"#f05454"},
                    {"range":[70,90],  "color":"#f5a623"},
                    {"range":[90,105], "color":"#4caf7d"},
                    {"range":[105,120],"color":"#7c83ff"},
                ],
                "threshold":{"line":{"color":"white","width":3},"thickness":0.75,"value":100},
                "bgcolor":COLORS["bg"],
            },
        ))
        fig_gauge.update_layout(
            paper_bgcolor=COLORS["bg"], font=dict(color="#e8eaf0"),
            margin=dict(t=40,b=20,l=20,r=20), height=340,
        )
        st.plotly_chart(fig_gauge, use_container_width=True)
else:
    st.info("Sem dados de budget no período selecionado.")

# ── Fluxo Despesas × Receitas ─────────────────────────────────────────────────
st.markdown('<div class="section-title">📉 Fluxo: Despesas × Receitas Mensais</div>', unsafe_allow_html=True)

if not fdf.empty:
    desp_m = fdf.groupby("AnoMes")["Saída(R$)"].sum().reset_index().rename(columns={"Saída(R$)":"Despesas"})
    entr_m = fdf.groupby("AnoMes")["Entrada(R$)"].sum().reset_index().rename(columns={"Entrada(R$)":"Receitas"})
    flux   = desp_m.merge(entr_m, on="AnoMes", how="outer").sort_values("AnoMes").fillna(0)
    flux["Saldo"] = flux["Receitas"] - flux["Despesas"]

    fig_flux = go.Figure()
    fig_flux.add_trace(go.Scatter(
        x=flux["AnoMes"], y=flux["Despesas"], name="Despesas",
        mode="lines+markers", line=dict(color=COLORS["danger"], width=2.5),
    ))
    fig_flux.add_trace(go.Scatter(
        x=flux["AnoMes"], y=flux["Receitas"], name="Receitas",
        mode="lines+markers", line=dict(color=COLORS["success"], width=2.5),
    ))
    fig_flux.add_trace(go.Bar(
        x=flux["AnoMes"], y=flux["Saldo"], name="Saldo",
        marker_color=[COLORS["success"] if v>=0 else COLORS["danger"] for v in flux["Saldo"]],
        opacity=0.4,
    ))
    fig_flux.update_layout(
        plot_bgcolor=COLORS["bg"], paper_bgcolor=COLORS["bg"],
        legend=dict(orientation="h", y=-0.22),
        xaxis=dict(tickangle=-45), yaxis_title="R$",
        margin=dict(t=10,b=70), font=dict(color="#e8eaf0"), template="plotly_dark",
    )
    st.plotly_chart(fig_flux, use_container_width=True)

# ── Tabela de Detalhes ────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📋 Detalhamento de Transações</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🔴 Despesas", "🟢 Budget Pessoal"])

with tab1:
    if not fdf.empty:
        cols_show = [c for c in ["Data Lançamento","DESCRIÇÃO","Saída(R$)","Entrada(R$)",
                                  "CC","CATEGORIA","GRUPO LABEL","STATUS","AnoMes"] if c in fdf.columns]
        show_df = fdf[cols_show].copy()
        if "Data Lançamento" in show_df.columns:
            show_df["Data Lançamento"] = show_df["Data Lançamento"].dt.strftime("%d/%m/%Y")
        for mc in ["Saída(R$)","Entrada(R$)"]:
            if mc in show_df.columns:
                show_df[mc] = show_df[mc].apply(lambda x: f"R$ {x:,.2f}" if x else "-")
        st.dataframe(show_df, use_container_width=True, height=360)
    else:
        st.info("Nenhuma transação no período.")

with tab2:
    if not bdf_range.empty:
        bshow = bdf_range.copy()
        bshow["Data Contábil"]    = bshow["Data Contábil"].dt.strftime("%d/%m/%Y")
        bshow["Entrada Real"]     = bshow["Entrada Real"].apply(lambda x: f"R$ {x:,.2f}" if x else "-")
        bshow["Entrada Esperada"] = bshow["Entrada Esperada"].apply(lambda x: f"R$ {x:,.2f}" if x else "-")
        st.dataframe(
            bshow[["Data Contábil","AnoMes","Título","Entrada Real","Entrada Esperada"]],
            use_container_width=True, height=360,
        )
    else:
        st.info("Nenhum registro de budget no período.")

# Footer
st.markdown("---")
st.caption(f"Dashboard Financeiro Pessoal · Ano de referência padrão: {CURRENT_YEAR}")
