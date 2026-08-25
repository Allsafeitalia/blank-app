# Inventario Aziendale

MVP per gestione inventario tramite barcode e QR code.

## Flusso

1. **Nuovo prodotto**: scansiona o inserisci il codice.
2. Inserisci nome, codice interno, unità per cartone e quantità iniziale.
3. **Inventario**: scansiona il codice e visualizza subito le unità disponibili.
4. **Movimenti**: registra carichi e scarichi.
5. **Prodotti**: consulta ed esporta il database.

## Demo su Streamlit

Imposta come main file `inventory_app.py` e usa il branch `inventario-aziendale-2026`.

## Nota

Il database SQLite è locale all'istanza dell'app. Per un uso aziendale reale va sostituito con un database persistente condiviso, ad esempio PostgreSQL, Supabase o un database aziendale.
