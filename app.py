import streamlit as st
import requests
import datetime as dt
import pandas as pd

# =========================
# CONFIG
# =========================
API_KEY = "sqlLjCJCt2A49AixsU2dpArdvFS5s1Xu"
API_SECRET = "eiINalYzDak1NEWn"

MAX_PRICE = 500
MAX_STOPS = 1

ORIGINS = ["BOD", "TLS", "CDG", "ORY", "BIQ"]
DESTINATIONS = ["GIG", "GRU", "SSA", "REC", "BSB", "FOR", "CNF"]

# =========================
# AUTH
# =========================
def get_token():
    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": API_KEY,
        "client_secret": API_SECRET
    }
    return requests.post(url, data=data).json()["access_token"]

# =========================
# SEARCH
# =========================
def search(origin, dest):
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    dep = (dt.date.today() + dt.timedelta(days=30)).isoformat()
    ret = (dt.date.today() + dt.timedelta(days=45)).isoformat()

    url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
    params = {
        "originLocationCode": origin,
        "destinationLocationCode": dest,
        "departureDate": dep,
        "returnDate": ret,
        "adults": 1,
        "currencyCode": "EUR",
        "max": 20
    }

    r = requests.get(url, headers=headers, params=params)
    return r.json().get("data", [])

# =========================
# UI
# =========================
st.title("✈️ Voos baratos França → Brasil")
st.caption("Filtro: até €500 | no máximo 1 escala")

if st.button("Buscar passagens"):
    results = []

    for o in ORIGINS:
        for d in DESTINATIONS:
            try:
                flights = search(o, d)
                for f in flights:
                    price = float(f["price"]["total"])
                    stops = len(f["itineraries"][0]["segments"]) - 1

                    if price <= MAX_PRICE and stops <= MAX_STOPS:
                        results.append([
                            o,
                            d,
                            price,
                            stops,
                            f["itineraries"][0]["segments"][0]["departure"]["at"][:10]
                        ])
            except:
                pass

    if results:
        df = pd.DataFrame(results, columns=["Origem", "Destino", "Preço (€)", "Escalas", "Data"])
        st.dataframe(df)
    else:
        st.warning("Nenhuma passagem abaixo de €500 com até 1 escala hoje.")
