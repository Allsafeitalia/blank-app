import streamlit as st
from datetime import date

st.set_page_config(page_title="FutureLife", page_icon="◉", layout="wide")

st.title("FutureLife")
st.caption("Un cruscotto personale per decidere meglio oggi, pensando a domani.")

if "future_items" not in st.session_state:
    st.session_state.future_items = [
        {"area": "Salute", "goal": "Allenamento", "impact": 5, "effort": 3, "deadline": date.today()},
        {"area": "Finanze", "goal": "Controllare spese", "impact": 4, "effort": 2, "deadline": date.today()},
    ]

st.subheader("Priorità di oggi")
for item in sorted(
    st.session_state.future_items,
    key=lambda x: x["impact"] / max(x["effort"], 1),
    reverse=True,
):
    score = round(item["impact"] / max(item["effort"], 1), 1)
    st.write(
        f"**{item['goal']}** · {item['area']} · "
        f"Priorità {score}/5 · entro {item['deadline'].strftime('%d/%m/%Y')}"
    )

st.divider()
st.subheader("Aggiungi una decisione")
with st.form("new_item"):
    area = st.selectbox(
        "Area",
        ["Salute", "Finanze", "Lavoro", "Famiglia", "Apprendimento", "Tempo libero"],
    )
    goal = st.text_input("Cosa vuoi ottenere?")
    impact = st.slider("Impatto futuro", 1, 5, 3)
    effort = st.slider("Sforzo", 1, 5, 3)
    deadline = st.date_input("Scadenza", date.today())
    submitted = st.form_submit_button("Aggiungi")

    if submitted and goal.strip():
        st.session_state.future_items.append(
            {
                "area": area,
                "goal": goal.strip(),
                "impact": impact,
                "effort": effort,
                "deadline": deadline,
            }
        )
        st.success("Decisione aggiunta.")

st.divider()
st.subheader("Il concetto")
st.markdown("""
FutureLife parte da un'idea semplice: nel 2026 avremo sempre più informazioni e sempre meno attenzione.
L'app aiuta a trasformare obiettivi, scadenze e decisioni in poche priorità concrete.

**Prossimi moduli:** diario delle decisioni, AI coach locale, simulazione scenari, integrazione calendario,
finanze e salute, memoria personale esportabile e modalità privacy-first.
""")
