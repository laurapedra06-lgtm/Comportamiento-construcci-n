# -*- coding: utf-8 -*-
"""
app.py — Expansión de la superficie construida en El Salvador
==================================================================
Aplicación de demostración construida con Streamlit.

PRINCIPIO DE DISEÑO
  Todo el cálculo pesado ocurre fuera de esta aplicación. Los rásters
  de GHSL y GLAD suman decenas de gigabytes y no caben en el entorno
  de despliegue, que dispone de alrededor de 1 GB de memoria.

  Por eso la app solo lee dos archivos CSV de unos pocos kilobytes,
  producidos previamente por los scripts de análisis. Las gráficas se
  generan al vuelo porque parten de tablas de treinta filas.

CÓMO EJECUTARLA EN LOCAL
    pip install streamlit pandas plotly
    streamlit run app.py

CÓMO PUBLICARLA
  1. Subir esta carpeta a un repositorio de GitHub
  2. Entrar a share.streamlit.io y conectar el repositorio
  3. Indicar app.py como archivo principal

ESTRUCTURA ESPERADA
    app.py
    requirements.txt
    datos/sv_serie.csv
    datos/regional.csv
==================================================================
"""

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ══════════════════════════════════════════════════════
DATOS = Path(__file__).parent / "datos"

NAVY, AZUL, SLATE = "#171640", "#1B3873", "#64798C"
NAR, VINO, VERDE = "#F49C66", "#8B3A42", "#2C6E49"
GRIS = "#D9DDE2"

COLOR = {"UC": NAVY, "UCL": NAR, "RUR": SLATE}
NOMBRE = {"UC": "Centros urbanos",
          "UCL": "Conglomerados urbanos",
          "RUR": "Resto del territorio"}
UMBRAL = {"UC": "≥ 1.500 hab/km² y 50.000 habitantes",
          "UCL": "≥ 300 hab/km² y 5.000 habitantes",
          "RUR": "no alcanza los umbrales anteriores"}
ORDEN = ["UC", "UCL", "RUR"]
# ══════════════════════════════════════════════════════

st.set_page_config(page_title="Expansión urbana · El Salvador",
                   page_icon="▪", layout="wide")

st.markdown(f"""
<style>
  .stApp {{ background-color: #FAFBFC; }}
  h1, h2, h3 {{ color: {NAVY}; }}
  [data-testid="stMetricValue"] {{ color: {NAVY}; font-size: 1.9rem; }}
  [data-testid="stMetricLabel"] {{ color: {SLATE}; }}
  .nota {{ color: {SLATE}; font-size: 0.78rem; line-height: 1.5; }}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def cargar():
    sv = pd.read_csv(DATOS / "sv_serie.csv")
    reg = pd.read_csv(DATOS / "regional.csv")
    return sv, reg


sv, reg = cargar()
bu = sv.pivot_table(index="epoca", columns="degurba",
                    values="construido_km2")[ORDEN]
bu["total"] = bu.sum(axis=1)
pob = sv.pivot_table(index="epoca", columns="degurba", values="poblacion")[ORDEN]
m2h = sv.pivot_table(index="epoca", columns="degurba", values="m2_por_hab")[ORDEN]

# ═══════════ CONTROLES ═══════════
with st.sidebar:
    st.markdown(f"### Parámetros")
    epocas = sorted(bu.index)
    ini, fin = st.select_slider(
        "Período de análisis", options=epocas, value=(2000, 2020))
    st.divider()
    st.markdown("**Grado de urbanización**")
    for c in ORDEN:
        st.markdown(
            f"<span style='color:{COLOR[c]};font-weight:bold'>■</span> "
            f"**{NOMBRE[c]}**<br><span class='nota'>{UMBRAL[c]}</span>",
            unsafe_allow_html=True)
    st.divider()
    st.markdown("<span class='nota'>Fuente: CEPAL sobre la base de "
                "JRC/Copernicus, GHS-COUNTRY-STATS R2024A y GHS-BUILT-S "
                "R2023A; GLAD/UMD, GLCLU2000-2020.</span>",
                unsafe_allow_html=True)

if ini == fin:
    st.warning("Selecciona un período con dos épocas distintas.")
    st.stop()

n = fin - ini
b0, b1 = bu.loc[ini], bu.loc[fin]
cagr = 100 * ((b1["total"] / b0["total"]) ** (1 / n) - 1)

# ═══════════ ENCABEZADO ═══════════
st.title("Expansión de la superficie construida")
st.markdown(f"<p style='color:{SLATE};font-size:1.05rem;margin-top:-0.6rem'>"
            f"El Salvador · {ini}–{fin}</p>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
c1.metric(f"Superficie en {ini}", f"{b0['total']:,.0f} km²".replace(",", "."))
c2.metric(f"Superficie en {fin}", f"{b1['total']:,.0f} km²".replace(",", "."),
          f"{100*(b1['total']/b0['total']-1):+.0f} %")
c3.metric("Tasa anual compuesta", f"{cagr:.2f} %")
c4.metric("Suelo incorporado",
          f"{b1['total']-b0['total']:,.0f} km²".replace(",", "."))

st.divider()

# ═══════════ PESTAÑAS ═══════════
t1, t2, t3, t4 = st.tabs(["Composición", "Dónde ocurrió",
                          "Suelo por habitante", "Comparación regional"])

# ---------- 1 ----------
with t1:
    st.subheader("¿Cómo se compone el suelo construido?")
    fig = go.Figure()
    for c in ORDEN:
        fig.add_trace(go.Scatter(
            x=bu.index, y=bu[c], name=NOMBRE[c], mode="lines",
            stackgroup="uno", line=dict(width=0.5, color="white"),
            fillcolor=COLOR[c],
            hovertemplate="%{y:.1f} km²<extra>" + NOMBRE[c] + "</extra>"))
    fig.add_vrect(x0=ini, x1=fin, fillcolor=VINO, opacity=0.07, line_width=0)
    fig.update_layout(
        height=430, hovermode="x unified", plot_bgcolor="white",
        yaxis_title="Superficie construida (km²)", xaxis_title=None,
        margin=dict(t=20, l=10, r=10, b=10),
        legend=dict(orientation="h", y=-0.15),
        font=dict(family="Helvetica, Arial", color=NAVY))
    fig.update_xaxes(gridcolor=GRIS); fig.update_yaxes(gridcolor=GRIS)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        f"<p class='nota'>El área sombreada marca el período seleccionado. "
        f"La superficie total pasó de {bu.loc[bu.index.min(),'total']:.0f} km² "
        f"en {bu.index.min()} a {bu.loc[bu.index.max(),'total']:.0f} km² en "
        f"{bu.index.max()}.</p>", unsafe_allow_html=True)

# ---------- 2 ----------
with t2:
    st.subheader("¿Dónde ocurrió la expansión?")
    inc = (b1[ORDEN] - b0[ORDEN])
    sh = 100 * inc / inc.sum()

    izq, der = st.columns([1.4, 1])
    with izq:
        fig = go.Figure()
        acum = 0
        for c in ORDEN:
            fig.add_trace(go.Bar(
                y=["incremento"], x=[sh[c]], name=NOMBRE[c], orientation="h",
                marker=dict(color=COLOR[c], line=dict(color="white", width=1.5)),
                text=[f"{sh[c]:.0f} %"], textposition="inside",
                insidetextanchor="middle",
                textfont=dict(color="white", size=15),
                hovertemplate=f"{inc[c]:.1f} km²<extra>{NOMBRE[c]}</extra>"))
            acum += sh[c]
        fig.update_layout(
            barmode="stack", height=190, plot_bgcolor="white",
            xaxis=dict(range=[0, 100], ticksuffix=" %", gridcolor=GRIS),
            yaxis=dict(showticklabels=False),
            margin=dict(t=10, l=10, r=10, b=10),
            legend=dict(orientation="h", y=-0.3),
            font=dict(family="Helvetica, Arial", color=NAVY))
        st.plotly_chart(fig, use_container_width=True)
    with der:
        for c in ORDEN:
            st.markdown(
                f"<span style='color:{COLOR[c]};font-weight:bold'>■</span> "
                f"{NOMBRE[c]}: **{inc[c]:.1f} km²** ({sh[c]:.0f} %)",
                unsafe_allow_html=True)

    st.markdown(
        "<p class='nota'>La clasificación por grado de urbanización se aplica "
        "a cada época, de modo que el aumento en centros urbanos recoge tanto "
        "edificación nueva como áreas que cambiaron de categoría al "
        "densificarse.</p>", unsafe_allow_html=True)

# ---------- 3 ----------
with t3:
    st.subheader("¿Cuánto suelo construido por habitante?")
    fig = go.Figure()
    for c in ORDEN:
        fig.add_trace(go.Scatter(
            x=m2h.index, y=m2h[c], name=NOMBRE[c], mode="lines+markers",
            line=dict(color=COLOR[c], width=2.6), marker=dict(size=6),
            hovertemplate="%{y:.0f} m²<extra>" + NOMBRE[c] + "</extra>"))
    fig.add_vrect(x0=ini, x1=fin, fillcolor=VINO, opacity=0.07, line_width=0)
    fig.update_layout(
        height=430, hovermode="x unified", plot_bgcolor="white",
        yaxis_title="Superficie construida por habitante (m²)",
        margin=dict(t=20, l=10, r=10, b=10),
        legend=dict(orientation="h", y=-0.15),
        font=dict(family="Helvetica, Arial", color=NAVY))
    fig.update_xaxes(gridcolor=GRIS); fig.update_yaxes(gridcolor=GRIS)
    st.plotly_chart(fig, use_container_width=True)

    cols = st.columns(3)
    for col, c in zip(cols, ORDEN):
        v0, v1 = m2h.loc[ini, c], m2h.loc[fin, c]
        col.metric(NOMBRE[c], f"{v1:.0f} m²", f"{100*(v1/v0-1):+.0f} %")

    st.markdown(
        "<p class='nota'>Un aumento implica que el suelo construido creció "
        "más rápido que la población. El valor del resto del territorio es "
        "mayor porque la población dispersa ocupa más suelo por persona.</p>",
        unsafe_allow_html=True)

# ---------- 4 ----------
with t4:
    st.subheader("El Salvador frente a la región")
    fuente = st.radio("Producto satelital", ["GHSL", "GLAD"],
                      horizontal=True, key="fuente")
    col = f"{fuente}_cagr_pct"

    d = reg.dropna(subset=[col]).sort_values(col)
    colores = [VINO if p == "El Salvador" else SLATE for p in d["pais"]]
    promedio = 100 * ((reg[f"{fuente}_2020_km2"].sum()
                       / reg[f"{fuente}_2000_km2"].sum()) ** 0.05 - 1)

    fig = go.Figure(go.Bar(
        y=d["pais"], x=d[col], orientation="h",
        marker=dict(color=colores),
        hovertemplate="%{x:.2f} % anual<extra>%{y}</extra>"))
    fig.add_vline(x=promedio, line=dict(color=VINO, width=1.6, dash="dash"),
                  annotation_text=f" ALC {promedio:.2f} %",
                  annotation_font=dict(color=VINO, size=12))
    fig.update_layout(
        height=760, plot_bgcolor="white", showlegend=False,
        xaxis_title="Tasa de crecimiento anual compuesta, 2000–2020 (%)",
        margin=dict(t=20, l=10, r=10, b=10),
        font=dict(family="Helvetica, Arial", color=NAVY))
    fig.update_xaxes(gridcolor=GRIS); fig.update_yaxes(gridcolor=GRIS)
    st.plotly_chart(fig, use_container_width=True)

    puesto = int((d[col] > d[d["pais"] == "El Salvador"][col].iloc[0]).sum()) + 1
    st.markdown(
        f"<p class='nota'>Con {fuente}, El Salvador ocupa el puesto "
        f"<b>{puesto} de {len(d)}</b> en la región. "
        "El ordenamiento de los países por tasa de crecimiento depende del "
        "producto empleado: GLAD registra territorio afectado por "
        "urbanización, incluidas vías, mientras que GHSL mide huella "
        "edificada de forma fraccional. Alterna entre ambos para ver el "
        "efecto.</p>", unsafe_allow_html=True)

# ═══════════ DESCARGA ═══════════
st.divider()
d1, d2 = st.columns(2)
d1.download_button("Descargar serie de El Salvador (CSV)",
                   sv.to_csv(index=False).encode("utf-8"),
                   "el_salvador_serie.csv", "text/csv")
d2.download_button("Descargar comparación regional (CSV)",
                   reg.to_csv(index=False).encode("utf-8"),
                   "comparacion_regional.csv", "text/csv")
