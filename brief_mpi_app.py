import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

# ---------- Funções auxiliares ----------
def export_pdf(data: dict) -> BytesIO:
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

def compute_brief_mpi_from_domains(domains: dict) -> dict:
    """Recebe um dict com os 8 valores (0,0.5,1) e devolve escore + risco"""
    vals = list(domains.values())
    mpi_raw = sum(vals) / 8
    if mpi_raw <= 0.33:
        risk = 'Mild (MPI 1)'
    elif mpi_raw <= 0.66:
        risk = 'Moderate (MPI 2)'
    else:
        risk = 'High (MPI 3)'
    return {"MPI": round(mpi_raw, 2), "risk": risk}

# ---------- Avaliação individual ----------
def avaliacao_individual():
    with st.expander("Responder às dimensões do Brief-MPI"):
    #st.subheader("Responder às dimensões do Brief-MPI")

        # ADL
        container = st.container(border=True)
        #with st.expander("Atividades básicas de vida diária (ADL)"):
        container.markdown("### Atividades básicas de vida diária (ADL)")
        cols = container.columns(3, border=True)
        adl_items = [
            cols[0].radio("Comer sozinho?", ["Sim", "Não"], key="adl1"),
            cols[1].radio("Vestir-se sozinho?", ["Sim", "Não"], key="adl2"),
            cols[2].radio("Controle de urina/fezes?", ["Sim", "Não"], key="adl3"),
        ]
        adl_score = sum([1 if x=="Sim" else 0 for x in adl_items])
        adl_value = 0 if adl_score == 3 else 0.5 if adl_score in [1,2] else 1

        st.divider()

        # IADL
        container =st.container(border=True)
        container.markdown("### Atividades instrumentais (IADL)")
        cols = container.columns(3, border=True)
        iadl_items = [
            cols[0].radio("Usa telefone sozinho?", ["Sim", "Não"], key="iadl1"),
            cols[1].radio("Responsável pela medicação?", ["Sim", "Não"], key="iadl2"),
            cols[2].radio("Faz compras sozinho?", ["Sim", "Não"], key="iadl3"),
        ]
        iadl_score = sum([1 if x=="Sim" else 0 for x in iadl_items])
        iadl_value = 0 if iadl_score == 3 else 0.5 if iadl_score in [1,2] else 1

        st.divider()

        # Mobilidade
        container = st.container(border=True)
        container.markdown("### Mobilidade")
        cols = container.columns(3, border=True)
        mobility_items = [
            cols[0].radio("Levantar-se sozinho?", ["Sim", "Não"], key="mob1"),
            cols[1].radio("Andar 3 metros?", ["Sim", "Não"], key="mob2"),
            cols[2].radio("Subir/descer escadas?", ["Sim", "Não"], key="mob3"),
        ]
        mobility_score = sum([1 if x=="Sim" else 0 for x in mobility_items])
        mobility_value = 0 if mobility_score >= 2 else 0.5 if mobility_score == 1 else 1

        st.divider()

        # Cognição
        container = st.container(border=True)
        container.markdown("### Cognição")
        cols = container.columns(3, border=True)
        cognitive_items = [
            cols[0].radio("Sabe a data?", ["Sim", "Não"], key="cog1"),
            cols[1].radio("Sabe a idade correta?", ["Sim", "Não"], key="cog2"),
            cols[2].radio("Conta de 20 para trás de 3 em 3?", ["Sim", "Não"], key="cog3"),
        ]
        cognitive_score = sum([0 if x=="Sim" else 1 for x in cognitive_items])
        cognitive_value = 0 if cognitive_score == 0 else 0.5 if cognitive_score == 1 else 1

        st.divider()

        # Nutrição
        container = st.container(border=True)
        container.markdown("### Estado nutricional")
        cols = container.columns(3, border=True)
        nutritional_items = [
            cols[0].radio("Perda de peso 3 meses?", ["Não", "Sim"], key="nut1"),
            cols[1].radio("IMC < 21?", ["Não", "Sim"], key="nut2"),
            cols[2].radio("Ingestão alimentar diminuída?", ["Não", "Sim"], key="nut3"),
        ]
        nutritional_score = sum([1 if x=="Sim" else 0 for x in nutritional_items])
        nutritional_value = 0 if nutritional_score == 0 else 0.5 if nutritional_score == 1 else 1

        st.divider()


        # Comorbidades
        col1, col2, col3 = st.columns(3)
        
        with col1:
            tile = col1.container(height=180, border=True)
            tile.markdown("### Comorbidades")
            comorbidities_count = tile.number_input("Nº de doenças crônicas:", min_value=0, step=1)
            comorb_value = 0 if comorbidities_count == 0 else 0.5 if comorbidities_count in [1,2] else 1

        # Fármacos 
        with col2:
            tile = col2.container(height=180, border=True)
            tile.markdown("### Medicamentos")
            drugs_count = tile.number_input("Nº de fármacos (princípios ativos):", min_value=0, step=2)
            drugs_value = 0 if drugs_count <= 3 else 0.5 if drugs_count <= 6 else 1
        
        # Co-habitação
        with col3:     
            tile = col3.container(height=180, border=True)
            tile.markdown("### Co-habitação")
            cohab = tile.radio("Vive com:", ["Com família", "Instituição", "Sozinho"])
            cohab_value = 0 if cohab=="Com família" else 0.5 if cohab=="Instituição" else 1
            
 
        st.divider()

        if st.button("Calcular MPI"):
            domains = {
                "ADL": adl_value,
                "IADL": iadl_value,
                "Mobility": mobility_value,
                "Cognitive": cognitive_value,
                "Nutritional": nutritional_value,
                "Comorbidity": comorb_value,
                "Drugs": drugs_value,
                "Cohabitation": cohab_value,
            }
            res = compute_brief_mpi_from_domains(domains)
            st.success(f"MPI = {res['MPI']} → {res['risk']}")

            # PDF
            pdf_buffer = export_pdf({**domains, **res})
            st.download_button("⬇️ Baixar relatório em PDF", data=pdf_buffer,
                               file_name="mpi_report.pdf", mime="application/pdf")

            # CSV
            csv = pd.DataFrame([{**domains, **res}]).to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Baixar relatório em CSV", data=csv,
                               file_name="mpi_report.csv", mime="text/csv")

# ---------- Carregar planilha ----------
def carregar_planilha():
    st.subheader("Carregar planilha com 8 dimensões já calculadas")

    file = st.file_uploader("Selecione um arquivo .csv ou .xlsx", type=["csv","xlsx"])
    if file:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)

        st.write("Prévia da planilha:")
        st.dataframe(df.head())

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
        st.download_button("⬇️ Baixar resultados em CSV", data=csv,
                           file_name="mpi_results.csv", mime="text/csv")

# ---------- App principal ----------

st.set_page_config(page_title="MPI", 
                   page_icon="🗂️",
                   layout="wide")


st.logo(image="logo/logo_projeto.png", size="large", link=None, icon_image=None)


col1, col2, col3 = st.columns(3)
with col1:
    st.title(":blue[Brief-MPI App]", width="content")
with col2:
    st.text("")    
with col3:
    st.image("logo/logo_projeto.png", width=200)


st.divider(width="stretch")
st.subheader("Índice Prognóstico Multidimensional (MPI) :receipt:", width="content")

multi = '''O *Índice Prognóstico Multidimensional (MPI)* é uma ferramenta prognóstica baseada 
na *Avaliação Multidimensional Geriátrica (VMD)*, que é o padrão de referência para a avaliação 
de pessoas idosas(com idade ≥ 65 anos). Diversos estudos sugerem a excelente precisão e 
calibração do MPI na previsão de desfechos negativos a curto e longo prazo, como hospitalização, 
institucionalização e mortalidade.

Esse app irá usar o Brief_MPI que é o modelo simplificado
 '''

st.markdown(multi)
st.divider(width="stretch")


mode = st.sidebar.radio("Escolha o modo:", ["📂 Carregar planilha", "📝 Avaliação individual"])

if mode == "📂 Carregar planilha":
    carregar_planilha()
else:
    avaliacao_individual()
st.divider(width="stretch")