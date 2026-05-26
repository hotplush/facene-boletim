import streamlit as st
import pypdf
import re

st.set_page_config(page_title="Calculadora de Boletim", page_icon="🎓")

st.title("🎓 Calculadora Automática de Boletim")
st.write("Arraste o PDF do seu quadro de atividades abaixo para ver sua situação.")

arquivo_pdf = st.file_uploader("Faça o upload do boletim (PDF)", type=["pdf"])

if arquivo_pdf is not None:
    try:
        leitor = pypdf.PdfReader(arquivo_pdf)
        texto_completo = ""
        for pagina in leitor.pages:
            texto_completo += pagina.extract_text() + "\n"
            
        linhas = texto_completo.strip().split('\n')
        
        disciplinas = {}
        disciplina_atual = None
        unidades_lidas = 0
        
        for linha in linhas:
            linha = linha.strip()
            if not linha: continue
            
            if "Quadro de atividades" in linha or linha == "Rep.":
                continue
                
            if "=" not in linha:
                disciplina_atual = linha
                disciplinas[disciplina_atual] = []
                unidades_lidas = 0
            else:
                if disciplina_atual and unidades_lidas < 3:
                    valores = re.findall(r'=\s*([\d.]+)', linha)
                    if valores:
                        soma_unidade = sum(float(v) for v in valores)
                        disciplinas[disciplina_atual].append(soma_unidade)
                        unidades_lidas += 1

        st.divider()
        st.subheader("📊 Seu Resultado:")
        
        for materia, notas in disciplinas.items():
            if not notas: continue 
            
            while len(notas) < 3:
                notas.append(0.0)
                
            un1, un2, un3 = notas[0], notas[1], notas[2]
            soma_total = round(un1 + un2 + un3, 1)
            
            with st.expander(f"📚 {materia} - Soma: {soma_total}"):
                st.write(f"**UN1:** {un1:.1f} | **UN2:** {un2:.1f} | **UN3:** {un3:.1f}")
                
                if soma_total >= 21.0:
                    st.success("🌟 STATUS: APROVADO DIRETO! (Média atingida, sem final)")
                elif soma_total >= 12.0:
                    st.info("🟢 STATUS: ELEGÍVEL PARA A FINAL (Já garantiu os 12 pontos)")
                else:
                    falta_para_final = round(12.0 - soma_total, 1)
                    falta_para_passar_direto = round(21.0 - soma_total, 1)
                    
                    if falta_para_final <= 10.0:
                        st.warning(f"🟡 STATUS: Faltam {falta_para_final} na UN3 para a Final.")
                        if falta_para_passar_direto <= 10.0:
                            st.write(f"💡 *Dica: Se tirar {falta_para_passar_direto} na UN3, passa DIRETO!*")
                    else:
                        st.error(f"🔴 STATUS: REPROVADO / REPOSIÇÃO (Matematicamente impossível chegar aos 12 apenas com a UN3).")
                        
    except Exception as e:
        st.error(f"Ocorreu um erro ao ler o arquivo: {e}")
