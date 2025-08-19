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
    vals = list(domains.values())
    mpi_raw = sum(vals) / 8
    if mpi_raw <= 0.33:
        risk = 'Mild (MPI 1)'
    elif mpi_raw <= 0.66:
        risk = 'Moderate (MPI 2)'
    else:
        risk = 'High (MPI 3)'
    return {"MPI": round(mpi_raw, 2), "risk": risk}

# ---------- Perguntas e lógica ----------
def avaliacao_individual():
    st.subheader("Responder às dimensões do Brief-MPI")

    # ADL
    st.markdown("### Atividades básicas de vida diária (ADL)")
    adl_items = [
        st.radio("O paciente consegue comer sozinho?", ["Sim", "Não"]),
        st.radio("O paciente consegue vestir-se sozinho?", ["Sim", "Não"]),
        st.radio("Controle de urina/fezes independente?", ["Sim", "Não"])
    ]
    adl_score = sum([1 if x=="Sim" else 0 for x in adl_items])
    if adl_score == 3:
        adl_value = 0
    elif adl_score in [1,2]:
        adl_value = 0.5
    else:
        adl_value = 1

    # IADL
    st.markdown("### Atividades instrumentais de vida diária (IADL)")
    iadl_items = [
        st.radio("É capaz de usar telefone sozinho?", ["Sim", "Não"]),
        st.radio("Responsável pela própria medicação?", ["Sim", "Não"]),
        st.radio("Faz compras sozinho?", ["Sim", "Não"])
    ]
    iadl_score = sum([1 if x=="Sim" else 0 for x in iadl_items])
    if iadl_score == 3:
        iadl_value = 0
    elif iadl_score in [1,2]:
        iadl_value = 0.5
    else:
        iadl_value = 1

    # Mobilidade
    st.markdown("### Mobilidade")
    mobility_items = [
        st.radio("Consegue levantar-se da cama/cadeira sozinho?", ["Sim", "Não"]),
        st.radio("Consegue andar pelo menos 3 metros (10 pés)?", ["Sim", "Não"]),
        st.radio("Consegue subir/descer escadas sem ajuda?", ["Sim", "Não"])
    ]
    mobility_score = sum([1 if x=="Sim" else 0 for x in mobility_items])
    if mobility_score >= 2:
        mobility_value = 0
    elif mobility_score == 1:
        mobility_value = 0.5
    else:
        mobility_value = 1

    # Cognitivo
    st.markdown("### Cognição")
    cognitive_items = [
        st.radio("Sabe a data (dia/mês/ano)?", ["Sim", "Não"]),
        st.radio("Sabe a idade correta?", ["Sim", "Não"]),
        st.radio("Consegue contar de 20 para trás de 3 em 3?", ["Sim", "Não"])
    ]
    cognitive_score = sum([0 if x=="Sim" else 1 for x in cognitive_items]) # erro conta
    if cognitive_score == 0:
        cognitive_value = 0
    elif cognitive_score == 1:
        cognitive_value = 0.5
    else:
        cognitive_value = 1

    # Nutrição
    st.markdown("### Estado nutricional")
    nutritional_items = [
        st.radio("Perda de peso nos últimos 3 meses?", ["Não", "Sim"]),
        st.radio("IMC < 21 kg/m2?", ["Não", "Sim"]),
        st.radio("Diminuição da ingestão alimentar?", ["Não", "Sim"])
    ]
    nutritional_score = sum([1 if x=="Sim" else 0 for x in nutritional_items])
    if nutritional_score == 0:
        nutritional_value = 0
    elif nutritional_score == 1:
        nutritional_value = 0.5
    else:
        nutritional_value = 1

    # Comorbidades
    st.markdown("### Comorbidades")
    comorbidities_count = st.number_input("Nº de doenças crônicas em tratamento:", min_value=0, step=1)
    if comorbidities_count == 0:
        comorb_value = 0
    elif comorbidities_count in [1,2]:
        comorb_value = 0.5
    else:
        comorb_value = 1

    # Fármacos
    st.markdown("### Medicamentos")
    drugs_count = st.number_input("Nº de fármacos em uso (princípios ativos):", min_value=0, step=1)
    if drugs_count <= 3:
        drugs_value = 0
    elif drugs_count <= 6:
        drugs_value = 0.5
    else:
        drugs_value = 1

    # Co-habitação
    st.markdown("### Co-habitação")
    cohab = st.radio("Com quem o paciente vive?", ["Com família", "Instituição", "Sozinho"])
    if cohab == "Com família":
        cohab_value = 0
    elif cohab == "Instituição":
        cohab_value = 0.5
    else:
        cohab_value = 1

    # Resultado final
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
        st.download_button("⬇️ Baixar relatório em PDF", data=pdf_buffer, file_name="mpi_report.pdf", mime="application/pdf")

        # CSV
        csv = pd.DataFrame([{**domains, **res}]).to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Baixar relatório em CSV", data=csv, file_name="mpi_report.csv", mime="text/csv")

