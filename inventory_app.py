import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

DB = "inventory.db"


def db():
    conn = sqlite3.connect(DB, check_same_thread=False)
    conn.execute("""CREATE TABLE IF NOT EXISTS products (
        barcode TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        product_code TEXT,
        units_per_carton INTEGER NOT NULL DEFAULT 1,
        cartons INTEGER NOT NULL DEFAULT 0,
        loose_units INTEGER NOT NULL DEFAULT 0,
        updated_at TEXT NOT NULL
    )""")
    conn.commit()
    return conn


conn = db()
st.set_page_config(page_title="Inventario Aziendale", page_icon="📦", layout="wide")
st.title("📦 Inventario Aziendale")
st.caption("Scansiona un codice, registra il prodotto e controlla subito le quantità.")

menu = st.sidebar.radio("Sezione", ["Inventario", "Nuovo prodotto", "Movimenti", "Prodotti"])


def decode_image(image):
    if image is None:
        return None
    try:
        import zxingcpp
        from PIL import Image
        results = zxingcpp.read_barcodes(Image.open(image))
        if results:
            return results[0].text
    except Exception as e:
        st.warning(f"Scansione non disponibile: {e}")
    return None


if menu == "Nuovo prodotto":
    st.header("Aggiungi prodotto")
    st.info("Puoi digitare il codice oppure fotografare il barcode/QR con la fotocamera del dispositivo.")

    col1, col2 = st.columns(2)
    with col1:
        barcode = st.text_input("Codice a barre / QR", placeholder="es. 8001234567890")
        photo = st.camera_input("Scansiona con la fotocamera")
        scanned = decode_image(photo)
        if scanned:
            st.success(f"Codice letto: {scanned}")
            barcode = scanned
    with col2:
        name = st.text_input("Nome prodotto")
        product_code = st.text_input("Codice prodotto interno (facoltativo)")
        units_per_carton = st.number_input("Unità per cartone", min_value=1, value=1, step=1)
        initial_cartons = st.number_input("Cartoni iniziali", min_value=0, value=0, step=1)
        initial_loose = st.number_input("Unità sfuse iniziali", min_value=0, value=0, step=1)

    if st.button("Salva prodotto", type="primary"):
        if not barcode.strip() or not name.strip():
            st.error("Inserisci almeno codice a barre e nome prodotto.")
        else:
            conn.execute("""INSERT OR REPLACE INTO products
                (barcode,name,product_code,units_per_carton,cartons,loose_units,updated_at)
                VALUES (?,?,?,?,?,?,?)""",
                (barcode.strip(), name.strip(), product_code.strip(), int(units_per_carton),
                 int(initial_cartons), int(initial_loose), datetime.now().isoformat(timespec="seconds")))
            conn.commit()
            st.success("Prodotto salvato nel database.")

elif menu == "Inventario":
    st.header("Controllo inventario")
    st.write("Scansiona o inserisci il codice per sapere subito quante unità sono disponibili.")

    barcode = st.text_input("Codice a barre / QR", key="inventory_barcode")
    photo = st.camera_input("Scansiona codice")
    scanned = decode_image(photo)
    if scanned:
        barcode = scanned
        st.success(f"Codice letto: {scanned}")

    if barcode:
        row = conn.execute("SELECT * FROM products WHERE barcode=?", (barcode.strip(),)).fetchone()
        if row:
            _, name, product_code, per_carton, cartons, loose, updated = row
            total = cartons * per_carton + loose
            st.subheader(name)
            c1, c2, c3 = st.columns(3)
            c1.metric("Unità disponibili", total)
            c2.metric("Cartoni", cartons)
            c3.metric("Unità sfuse", loose)
            st.caption(f"{total} unità = {cartons} cartoni × {per_carton} + {loose} sfuse")
            if product_code:
                st.write(f"Codice prodotto: **{product_code}**")
        else:
            st.warning("Codice non presente nel database. Aggiungilo dalla sezione Nuovo prodotto.")

elif menu == "Movimenti":
    st.header("Carico / scarico")
    barcode = st.text_input("Codice prodotto")
    row = conn.execute("SELECT name, units_per_carton, cartons, loose_units FROM products WHERE barcode=?", (barcode.strip(),)).fetchone() if barcode else None
    if row:
        name, per_carton, cartons, loose = row
        st.write(f"**{name}** · disponibilità: **{cartons * per_carton + loose} unità**")
        movement = st.radio("Movimento", ["Carico", "Scarico"], horizontal=True)
        quantity = st.number_input("Quantità di unità", min_value=1, value=1, step=1)
        if st.button("Registra movimento", type="primary"):
            total = cartons * per_carton + loose
            new_total = total + quantity if movement == "Carico" else total - quantity
            if new_total < 0:
                st.error("Quantità insufficiente in magazzino.")
            else:
                new_cartons, new_loose = divmod(new_total, per_carton)
                conn.execute("UPDATE products SET cartons=?, loose_units=?, updated_at=? WHERE barcode=?",
                             (new_cartons, new_loose, datetime.now().isoformat(timespec="seconds"), barcode.strip()))
                conn.commit()
                st.success(f"Movimento registrato. Nuova disponibilità: {new_total} unità.")
    elif barcode:
        st.warning("Prodotto non trovato.")

elif menu == "Prodotti":
    st.header("Database prodotti")
    df = pd.read_sql_query("SELECT barcode AS 'Barcode', name AS 'Prodotto', product_code AS 'Codice prodotto', units_per_carton AS 'Unità/cartone', cartons AS 'Cartoni', loose_units AS 'Sfuse', (units_per_carton * cartons + loose_units) AS 'Totale unità' FROM products ORDER BY name", conn)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.download_button("Esporta CSV", df.to_csv(index=False), "inventario.csv", "text/csv")
