import json
from datetime import date
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="FutureLife", page_icon="◉", layout="wide")

DATA_FILE = Path("futurelife_data.json")
AREAS = ["Salute", "Finanze", "Lavoro", "Famiglia", "Apprendimento", "Tempo libero"]


def load_items():
    if not DATA_FILE.exists():
        return [
            {"area": "Salute", "goal": "Allenamento", "impact": 5, "effort": 3, "deadline": date.today().isoformat()},
            {"area": "Finanze", "goal": "Controllare spese", "impact": 4, "effort": 2, "deadline": date.today().isoformat()},
        ]

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            items = json.load(file)
        return items if isinstance(items, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def save_items(items):
    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(items, file, ensure_ascii=False, indent=2)


if "future_items" not in st.session_state:
    st.session_state.future_items = load_items()

st.title("FutureLife")
st.caption("Un cruscotto personale per decidere meglio oggi, pensando a domani.")

st.subheader("Priorità di oggi")

items = sorted(
    st.session_state.future_items,
    key=lambda item: item["impact"] / max(item["effort"], 1),
    reverse=True,
)

if not items:
    st.info("Non ci sono ancora decisioni.")
else:
    for item in items:
        score = round(item["impact"] / max(item["effort"], 1), 1)
        deadline = date.fromisoformat(item["deadline"]).strftime("%d/%m/%Y")
        st.write(
            f"**{item['goal']}** · {item['area']} · "
            f"Priorità {score}/5 · entro {deadline}"
        )

st.divider()
st.subheader("Aggiungi una decisione")

with st.form("new_item"):
    area = st.selectbox("Area", AREAS)
    goal = st.text_input("Cosa vuoi ottenere?")
    impact = st.slider("Impatto futuro", 1, 5, 3)
    effort = st.slider("Sforzo", 1, 5, 3)
    deadline = st.date_input("Scadenza", date.today())
    submitted = st.form_submit_button("Aggiungi")

    if submitted:
        if not goal.strip():
            st.error("Inserisci un obiettivo.")
        else:
            st.session_state.future_items.append(
                {
                    "area": area,
                    "goal": goal.strip(),
                    "impact": impact,
                    "effort": effort,
                    "deadline": deadline.isoformat(),
                }
            )
            save_items(st.session_state.future_items)
            st.success("Decisione aggiunta e salvata.")
            st.rerun()

st.divider()
st.subheader("Il concetto")
st.markdown(
    """
FutureLife parte da un'idea semplice: nel 2026 avremo sempre più informazioni e sempre meno attenzione.
L'app aiuta a trasformare obiettivi, scadenze e decisioni in poche priorità concrete.

**Prossimi moduli:** diario delle decisioni, AI coach locale, simulazione scenari, integrazione calendario,
finanze e salute, memoria personale esportabile e modalità privacy-first.
"""
)
