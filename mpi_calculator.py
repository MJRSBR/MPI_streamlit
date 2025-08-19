import streamlit as st
import pandas as pd
from fpdf import FPDF
import io

# Função para calcular o MPI a partir das 8 dimensões
def calcular_mpi(dimensoes: list) -> float:
    return round(sum(dimensoes) / len(dimensoes), 2)

def interpretar_mpi(mpi: float) -> str:
    if mpi <= 0.33:
        return "Baixo risco (MPI 1)"
    elif mpi <= 0.66:
        return "Risco moderado (MPI 2)"
    else:
        return "Alto risco (MPI 3)"

# Função para gerar relatório PDF
def gerar_pdf(nome, instituicao, dimensoes, mpi, interpretacao):
    buffer = io.BytesIO()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, f"Relatório MPI - {nome}", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, f"Instituição: {instituicao}", ln=True)
    
    for i, val in enumerate(dimensoes, start=1):
        pdf.cell(200, 10, f"Dimensão {i}: {val}", ln=True)
    
    pdf.ln(5)
    pdf.cell(200, 10, f"Escore MPI: {mpi}", ln=True)
    pdf.cell(200, 10, f"Classificação: {interpretacao}", ln=True)

    pdf.output(buffer)
    buffer.seek(0)
    return buffer


# Streamlit App
st.title("📊 Brief-MPI Calculator")

opcao = st.sidebar.radio("Escolha o modo de uso:", 
                         ["📂 Carregar Planilha", "✍️ Inserir Manualmente"])

# --- MODO 1: CARREGAR PLANILHA ---
if opcao == "📂 Carregar Planilha":
    st.header("Carregar Planilha com Dimensões")
    uploaded_file = st.file_uploader("Carregue um arquivo CSV ou Excel", type=["csv", "xlsx"])

    if uploaded_file:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.write("Pré-visualização dos dados carregados:")
        st.dataframe(df.head())

        if all(col in df.columns for col in [f"dim{i}" for i in range(1, 9)]):
            df["MPI"] = df[[f"dim{i}" for i in range(1, 9)]].mean(axis=1).round(2)
            df["Classificação"] = df["MPI"].apply(interpretar_mpi)

            st.success("MPI calculado com sucesso!")
            st.dataframe(df)

            # Exportar CSV
            csv_buffer = io.BytesIO()
            df.to_csv(csv_buffer, index=False)
            st.download_button("📥 Baixar resultados em CSV", 
                               data=csv_buffer.getvalue(), 
                               file_name="resultados_mpi.csv", 
                               mime="text/csv")
        else:
            st.error("A planilha deve conter as colunas: dim1, dim2, ..., dim8")

# --- MODO 2: INSERIR MANUALMENTE ---
elif opcao == "✍️ Inserir Manualmente":
    st.header("Inserir Dados Manualmente")

    nome = st.text_input("Nome do paciente")
    instituicao = st.text_input("Instituição")
    
    st.subheader("Preencher valores das 8 dimensões")
    dimensoes = []
    for i in range(1, 9):
        val = st.selectbox(f"Dimensão {i}", [0, 0.5, 1], key=f"dim{i}")
        dimensoes.append(val)

    if st.button("Calcular MPI"):
        mpi = calcular_mpi(dimensoes)
        interpretacao = interpretar_mpi(mpi)

        st.success(f"📊 MPI = {mpi} → {interpretacao}")

        # Criar DataFrame para exportar
        df_paciente = pd.DataFrame([{
            "Nome": nome,
            "Instituição": instituicao,
            **{f"Dimensão {i+1}": dimensoes[i] for i in range(8)},
            "MPI": mpi,
            "Classificação": interpretacao
        }])

        # Exportar CSV
        csv_buffer = io.BytesIO()
        df_paciente.to_csv(csv_buffer, index=False)
        st.download_button("📥 Baixar em CSV", 
                           data=csv_buffer.getvalue(), 
                           file_name="mpi_paciente.csv", 
                           mime="text/csv")

        # Exportar PDF
        pdf_buffer = gerar_pdf(nome, instituicao, dimensoes, mpi, interpretacao)
        st.download_button("📄 Baixar Relatório em PDF", 
                           data=pdf_buffer, 
                           file_name="mpi_relatorio.pdf", 
                           mime="application/pdf")



import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

# ---------- Funções auxiliares ----------
from typing import Dict, Any
def compute_brief_mpi_from_domains(domains: Dict[str, Any]) -> Dict[str, Any]:
    """Recebe um dicionário com as 8 dimensões (já codificadas como 0,0.5,1) e retorna MPI e risco."""
    vals = list(domains.values())
    mpi_raw = sum(vals) / 8
    if mpi_raw <= 0.33:
        risk = 'Mild (MPI 1)'
    elif mpi_raw <= 0.66:
        risk = 'Moderate (MPI 2)'
    else:
        risk = 'High (MPI 3)'
    return {"MPI": round(mpi_raw, 2), "risk": risk}

def export_pdf(data: Dict[str, Any]) -> BytesIO:
    """Gera PDF simples com resumo"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph("Relatório Brief-MPI", styles["Title"]))
    story.append(Spacer(1, 12))
    for k,v in data.items():
        story.append(Paragraph(f"<b>{k}:</b> {v}", styles["Normal"]))
        story.append(Spacer(1, 6))
    doc.build(story)
    buffer.seek(0)
    return buffer

# ---------- App ----------
st.title("Brief-MPI App")

mode = st.sidebar.radio("Escolha o modo:", ["📂 Carregar planilha", "📝 Avaliação individual"])

if mode == "📂 Carregar planilha":
    st.subheader("Carregar planilha com 8 dimensões já calculadas")

    file = st.file_uploader("Selecione um arquivo .csv ou .xlsx", type=["csv","xlsx"])
    if file:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        st.write("Prévia da planilha:")
        st.dataframe(df.head())

        # Espera que as colunas sejam ADL, IADL, Mobility, Cognitive, Nutritional, Comorbidity, Drugs, Cohab
        results = []
        for _, row in df.iterrows():
            domains = {
                "ADL": row["ADL"],
                "IADL": row["IADL"],
                "Mobility": row["Mobility"],
                "Cognitive": row["Cognitive"],
                "Nutritional": row["Nutritional"],
                "Comorbidity": row["Comorbidity"],
                "Drugs": row["Drugs"],
                "Cohabitation": row["Cohabitation"]
            }
            res = compute_brief_mpi_from_domains(domains)
            results.append(res)

        res_df = pd.concat([df.reset_index(drop=True), pd.DataFrame(results)], axis=1)
        st.dataframe(res_df)

        # Exportar CSV
        csv = res_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Baixar resultados em CSV", data=csv, file_name="mpi_results.csv", mime="text/csv")

elif mode == "📝 Avaliação individual":
    st.subheader("Responder as dimensões")

    adl = st.selectbox("ADL (0=alto risco, 0.5=médio, 1=baixo)", [0,0.5,1])
    iadl = st.selectbox("IADL", [0,0.5,1])
    mobility = st.selectbox("Mobilidade", [0,0.5,1])
    cognitive = st.selectbox("Cognitivo", [0,0.5,1])
    nutritional = st.selectbox("Nutrição", [0,0.5,1])
    comorbidity = st.selectbox("Comorbidades", [0,0.5,1])
    drugs = st.selectbox("Nº de fármacos", [0,0.5,1])
    cohab = st.selectbox("Co-habitação", [0,0.5,1])

    if st.button("Calcular MPI"):
        domains = {
            "ADL": adl,
            "IADL": iadl,
            "Mobility": mobility,
            "Cognitive": cognitive,
            "Nutritional": nutritional,
            "Comorbidity": comorbidity,
            "Drugs": drugs,
            "Cohabitation": cohab,
        }
        res = compute_brief_mpi_from_domains(domains)
        st.success(f"MPI = {res['MPI']} → {res['risk']}")

        # Exportar PDF
        pdf_buffer = export_pdf({**domains, **res})
        st.download_button("⬇️ Baixar relatório em PDF", data=pdf_buffer, file_name="mpi_report.pdf", mime="application/pdf")

        # Exportar CSV
        csv = pd.DataFrame([{**domains, **res}]).to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Baixar relatório em CSV", data=csv, file_name="mpi_report.csv", mime="text/csv")