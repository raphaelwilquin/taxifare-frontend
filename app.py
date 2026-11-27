import base64
import math
import json
import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import requests
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="TaxiFare NYC | Estimation de taxi", page_icon="🚕", layout="wide")

NY = ZoneInfo("America/New_York")

PLACES = {
    "Empire State Building": (40.7484, -73.9857),
    "Central Park · Metropolitan Museum": (40.7850, -73.9680),
    "Times Square": (40.7580, -73.9855),
    "Grand Central Terminal": (40.7527, -73.9772),
    "One World Trade Center": (40.7127, -74.0134),
    "Brooklyn · DUMBO": (40.7033, -73.9881),
    "Aéroport JFK": (40.6413, -73.7781),
    "Aéroport LaGuardia": (40.7769, -73.8740),
    "Queens · Flushing": (40.7596, -73.8303),
    "Bronx · Yankee Stadium": (40.8296, -73.9262),
}
CUSTOM = "Saisir des coordonnées GPS"

CSS = """
<style>
:root { --ink:#172334; --muted:#536174; --yellow:#ffce32; }
.stApp { background:#f5f5f1; color:var(--ink); }
[data-testid="stHeader"] {background:transparent;}
[data-testid="stAppViewBlockContainer"], .block-container {max-width:1240px; padding-top:2.3rem; padding-bottom:2rem;}
[data-testid="stVerticalBlock"] {gap:.85rem;}
.nyc-brand {display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom:5px;}
.brand-main {font-size:23px; font-weight:850; letter-spacing:-1.2px; color:#172334; display:flex; align-items:center; gap:9px;}
.brand-mark {display:inline-flex; align-items:center; justify-content:center; width:34px;height:34px;background:#ffce32;border-radius:9px;font-size:20px;}
.brand-tag {font-size:11px;font-weight:750;letter-spacing:1.5px;color:#536174;text-transform:uppercase;text-align:right;}
.hero {position:relative;overflow:hidden;isolation:isolate;background:linear-gradient(110deg,#111d2e 0%,#182a43 65%,#21364d 100%);border-radius:22px;min-height:264px;padding:36px 38px;display:flex;align-items:center;box-shadow:0 15px 35px #14223815;}
.hero-copy {position:relative;z-index:2;max-width:590px;}
.hero-kicker {display:inline-block;color:#ffda62;font-size:11px;font-weight:800;letter-spacing:2.3px;text-transform:uppercase;margin-bottom:14px;}
.hero h1 {font-size:clamp(32px,4.5vw,55px);letter-spacing:-2.6px;line-height:1.02;color:#fff;margin:0 0 13px;padding:0;font-weight:850;}
.hero h1 span {color:#ffce32;}
.hero p {font-size:15px;line-height:1.6;color:#e0e8f1;max-width:410px;margin:0;}
.hero-art {position:absolute;z-index:0;right:0;bottom:0;width:59%;height:100%;opacity:.95;background-repeat:no-repeat;background-position:right bottom;background-size:cover;}
.hero::after {content:'';position:absolute;z-index:1;inset:0;background:linear-gradient(90deg,#111d2e 0%,#111d2e00 75%);pointer-events:none;}
.eyebrow {font-size:10px;font-weight:850;letter-spacing:1.7px;color:#746018;text-transform:uppercase;margin:0 0 5px;}
.panel-title {font-size:23px;font-weight:800;letter-spacing:-.7px;color:#172334;line-height:1.15;}
.panel-sub {font-size:13px;color:#536174;margin-top:4px;line-height:1.45;}
.st-key-trip_panel, .st-key-map_panel {background:#fff;border-radius:18px;padding:19px;box-shadow:0 5px 18px #182a4309;border:1px solid #e5e7e9;}
.st-key-trip_panel label p {font-weight:650;color:#263648;font-size:13px;}
.st-key-trip_panel [data-baseweb="select"] > div, .st-key-trip_panel [data-baseweb="input"] {background:#f8f9fb;border-color:#dbe1e7;border-radius:9px;}
.st-key-trip_panel [data-baseweb="select"] input, .st-key-trip_panel input {color:#172334;}
.st-key-trip_panel [data-testid="stButton"] button {width:100%;background:#ffce32;color:#172334;border:1px solid #ffce32;border-radius:10px;min-height:49px;font-weight:800;box-shadow:0 4px 12px #f0bb0024;}
.st-key-trip_panel [data-testid="stButton"] button:hover {background:#ffdc66;color:#172334;border-color:#ae8500;}
.st-key-trip_panel [data-testid="stButton"] button:focus-visible {outline:3px solid #172334;outline-offset:2px;}
.map-frame {display:flex;gap:14px;flex-wrap:wrap;font-size:12px;color:#536174;align-items:center;}
.dot {display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:5px;}
.dot-a {background:#d39a00;} .dot-b {background:#008b82;}
.fare-card {background:#172334;color:#fff;border-radius:16px;padding:19px 22px;position:relative;overflow:hidden;border:1px solid #263c55;}
.fare-card:after {content:'';position:absolute;right:-13px;top:-17px;width:110px;height:110px;opacity:.12;background:repeating-linear-gradient(45deg,#ffce32 0 12px,transparent 12px 24px);transform:rotate(-9deg);pointer-events:none;}
.fare-kicker {font-size:10px;font-weight:800;letter-spacing:1.6px;color:#ffda62;}
.fare-amount {font-size:clamp(32px,5vw,48px);font-weight:850;letter-spacing:-2px;line-height:1.15;margin:8px 0 6px;color:#ffce32;}
.fare-caption {font-size:12px;color:#d5e0eb;line-height:1.45;max-width:90%;}
.footer {border-top:1px solid #dce0e4;margin-top:15px;padding:15px 0 0;color:#536174;font-size:11px;display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;}
@media (max-width:650px){.block-container {padding:1.4rem .9rem;} .hero {padding:25px 20px;min-height:290px;align-items:flex-start;} .hero h1 {letter-spacing:-1.3px;} .hero-art {width:100%;height:60%;opacity:.48;} .hero::after {background:linear-gradient(180deg,#111d2e 15%,transparent 100%);} .brand-tag {font-size:9px;} .st-key-trip_panel,.st-key-map_panel {padding:13px;}}
</style>
"""


HERO = """
<div class="nyc-brand"><div class="brand-main"><span class="brand-mark">🚕</span>TaxiFare<span style="color:#987000">NYC</span></div><div class="brand-tag">New York City / États-Unis</div></div>
<div class="hero">
<div class="hero-copy"><div class="hero-kicker">40°43′ N · 74°00′ O &nbsp; / &nbsp; NYC</div><h1>New York,<br>à portée de <span>taxi.</span></h1><p>De Manhattan à Brooklyn, estimez le prix de votre course en quelques secondes.</p></div>
<svg class="hero-art" viewBox="0 0 680 280" preserveAspectRatio="xMaxYMax slice" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">
<defs><linearGradient id="cityFade" x1="0" x2="0" y1="0" y2="1"><stop stop-color="#48627f"/><stop offset="1" stop-color="#253b55"/></linearGradient><pattern id="windows" width="14" height="17" patternUnits="userSpaceOnUse"><rect x="3" y="4" width="3" height="5" fill="#f8d37b" opacity=".5"/></pattern><linearGradient id="taxiPaint" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#ffe06b"/><stop offset="1" stop-color="#eeb400"/></linearGradient></defs>
<circle cx="513" cy="91" r="78" fill="#ffce32" opacity=".12"/><circle cx="513" cy="91" r="67" fill="#ffce32" opacity=".13"/>
<g fill="#b7c9da" opacity=".55"><circle cx="323" cy="36" r="1.5"/><circle cx="610" cy="27" r="2"/><circle cx="458" cy="22" r="1.5"/><circle cx="644" cy="72" r="1.5"/><circle cx="206" cy="76" r="1.6"/></g>
<path d="M0 239V165H35V142H64V177H93V120H128V158H158V103H199V160H223V83H250V168H275V128H313V172H350V104H386V158H414V131H457V176H483V114H512V156H545V102H569V145H604V132H639V175H680V239Z" fill="#304963" opacity=".8"/>
<g fill="url(#cityFade)"><path d="M138 237V138H190V237Z"/><path d="M201 237V102H243V237Z"/><path d="M264 237V79H279V57H291V43H296V11H300V43H305V57H317V79H332V237Z"/><path d="M347 237V148H387V237Z"/><path d="M406 237V107H416V91Q420 81 430 78Q434 64 443 55V32H447V55Q456 64 460 78Q470 81 474 91V107H484V237Z"/><path d="M501 237V79L535 45L565 79V237Z"/><path d="M590 237V120H635V237Z"/><path d="M644 237V167H680V237Z"/></g>
<g fill="url(#windows)"><path d="M146 146H182V227H146Z"/><path d="M207 110H237V227H207Z"/><path d="M272 87H324V230H272Z"/><path d="M352 154H381V227H352Z"/><path d="M413 111H477V227H413Z"/><path d="M508 86H558V230H508Z"/><path d="M596 127H628V230H596Z"/></g>
<g stroke="#f1c65b" stroke-width="1.5" fill="none" opacity=".9"><path d="M279 79H317M285 57H311M291 43H305M296 11H300"/><path d="M420 91Q445 67 470 91M416 102Q445 78 474 102M431 78Q445 61 459 78M445 32V18"/><path d="M535 45V12M501 79L535 45L565 79"/></g>
<path d="M0 238H680V280H0Z" fill="#101c2b"/><path d="M0 239H680" stroke="#8096aa" opacity=".45"/><path d="M0 271H680" stroke="#ffd86e" stroke-dasharray="28 22" opacity=".5"/>
<!-- Statue de la Liberté, silhouette stylisée -->
<g fill="#82a99f"><path d="M105 238H151V229H145V222H111V229H105Z"/><path d="M116 222L120 190L113 173L119 158L111 145L105 128L108 120L115 122L122 140L128 153L138 155L147 169L140 184L147 222Z"/><circle cx="133" cy="145" r="7"/><path d="M126 140L121 132L129 137L130 127L134 136L140 128L139 138L147 134L141 143Z"/><path d="M105 128L99 114H105L111 125Z"/><path d="M101 114Q94 108 101 99Q102 106 107 109L106 114Z" fill="#ffce32"/></g>
<!-- Taxi jaune au premier plan -->
<g transform="translate(392 197)"><ellipse cx="113" cy="53" rx="115" ry="8" fill="#000" opacity=".35"/><path d="M7 30Q10 19 26 18L49 6Q54 2 67 2H139Q150 2 158 9L181 24L205 29Q216 32 218 42V48H3V39Q3 34 7 30Z" fill="url(#taxiPaint)" stroke="#f5ca42" stroke-width="1.5"/><path d="M55 8H94V23H36ZM102 8H139Q145 8 151 14L166 23H102Z" fill="#263c55"/><path d="M96 26V44M169 27V44" stroke="#a97800" opacity=".6"/><rect x="88" y="-5" width="36" height="8" rx="2" fill="#ffde70"/><text x="106" y="1" text-anchor="middle" font-size="6" font-weight="bold" fill="#172334">TAXI</text><g fill="#172334"><circle cx="44" cy="48" r="13"/><circle cx="181" cy="48" r="13"/><rect x="108" y="30" width="24" height="5"/></g><g fill="#8393a4"><circle cx="44" cy="48" r="5"/><circle cx="181" cy="48" r="5"/></g><rect x="6" y="34" width="10" height="5" rx="2" fill="#fff0b5"/><rect x="207" y="34" width="10" height="5" rx="2" fill="#f78255"/></g>
</svg></div>
"""


def panel_header(step, title, subtitle):
    st.html(f'<div class="eyebrow">{step}</div><div class="panel-title">{title}</div><div class="panel-sub">{subtitle}</div>')


def select_place(label, default, key):
    options = list(PLACES) + [CUSTOM]
    choice = st.selectbox(label, options, index=options.index(default), key=f"{key}_place")
    if choice == CUSTOM:
        col_lat, col_lon = st.columns(2)
        lat = col_lat.number_input("Latitude", min_value=40.45, max_value=40.95, value=PLACES[default][0], format="%.6f", step=0.0001, key=f"{key}_lat")
        lon = col_lon.number_input("Longitude", min_value=-74.30, max_value=-73.65, value=PLACES[default][1], format="%.6f", step=0.0001, key=f"{key}_lon")
        return (lat, lon)
    return PLACES[choice]


def normalize_url(value):
    url = value.strip().rstrip("/")
    if not url.startswith(("https://", "http://")):
        raise ValueError("URL API invalide")
    return url if url.endswith("/predict") else url + "/predict"


def pickup_utc(date, time):
    """Convertit l'heure de New York en UTC ; rejette les heures DST ambiguës."""
    naive = datetime.combine(date, time)
    candidates = set()
    for fold in (0, 1):
        local = naive.replace(tzinfo=NY, fold=fold)
        utc = local.astimezone(timezone.utc)
        if utc.astimezone(NY).replace(tzinfo=None) == naive:
            candidates.add(utc)
    if len(candidates) != 1:
        raise ValueError("Cette heure est ambiguë ou inexistante à New York (changement d’heure). Choisissez une autre heure.")
    return candidates.pop().strftime("%Y-%m-%d %H:%M:%S UTC")


def get_fare(params):
    API_URL = os.getenv("API_URL") or st.secrets["API_URL"]
    response = requests.get(normalize_url(API_URL), params=params, timeout=15)
    response.raise_for_status()
    fare = float(response.json()["fare"])
    if not math.isfinite(fare) or fare < 0:
        raise ValueError("Tarif invalide")
    return fare


def draw_map(start, end):
    coords = json.dumps([list(start), list(end)], allow_nan=False)
    html = r"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="referrer" content="strict-origin-when-cross-origin">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="">
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
<style>
html,body{margin:0;height:100%;font-family:Arial,sans-serif}
.leaflet-control-attribution{font-size:10px}
.leaflet-tooltip{font-weight:700;border-radius:6px}
</style></head><body><div id="map" aria-label="Carte aérienne de New York"></div><div id="notice" role="status"></div>
<script>
const points = __POINTS__;
const map = L.map('map', {minZoom:9,maxZoom:21,scrollWheelZoom:false,zoomControl:true});
const photo = L.tileLayer('https://tiles.arcgis.com/tiles/yG5s3afENB5iO9fj/arcgis/rest/services/NYC_Orthos_2024/MapServer/tile/{z}/{y}/{x}', {maxZoom:21,attribution:'Photographies aériennes 2024 © <a href="https://gis.nyc.gov/tiles/" target="_blank" rel="noopener">NYC OTI</a>'});
const streets = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {maxNativeZoom:19,maxZoom:21,attribution:'© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a> contributors'});
L.control.layers({'Vue aérienne':photo,'Plan de ville':streets},null,{position:'topright',collapsed:false}).addTo(map);
L.polyline(points,{color:'
L.polyline(points,{color:'
points.forEach((p,i)=>L.circleMarker(p,{radius:8,color:'
const fitTrip = ()=>{map.invalidateSize({pan:false});map.fitBounds(L.latLngBounds(points),{padding:[38,38],maxZoom:17});};
fitTrip();
let previousSize = '';
if (typeof ResizeObserver !== 'undefined') {
  new ResizeObserver(()=>{const el=map.getContainer();const size=el.clientWidth+'x'+el.clientHeight;if(size!==previousSize && el.clientWidth && el.clientHeight){previousSize=size;fitTrip();}}).observe(map.getContainer());
}
const notice=document.getElementById('notice');
photo.on('tileerror',()=>{if(map.hasLayer(photo)){notice.textContent='Certaines photos ne sont pas disponibles. Vous pouvez essayer le plan de ville.';notice.style.display='block';}});
streets.on('tileerror',()=>{if(map.hasLayer(streets)){notice.textContent='Le plan de ville est temporairement indisponible. Essayez la vue aérienne.';notice.style.display='block';}});
map.on('baselayerchange',()=>{notice.style.display='none';});
photo.addTo(map);
</script></body></html>"""
    components.html(html.replace("__POINTS__", coords), height=365, scrolling=False)
    st.html('<div class="map-frame"><span><i class="dot dot-a"></i>Départ</span><span><i class="dot dot-b"></i>Arrivée</span><span>Trait indicatif · à vol d’oiseau</span></div>')


def show_result(fare):
    if fare is None:
        amount = "—"
        note = "Renseignez votre trajet puis lancez une estimation pour découvrir votre tarif."
    else:
        amount = f"{fare:,.2f}".replace(",", " ").replace(".", ",") + " $"
        note = "Estimation en dollars américains (USD). Le montant réel peut varier."
    st.html(f'<div class="fare-card" role="status"><div class="fare-kicker">03 / VOTRE ESTIMATION</div><div class="fare-amount">{amount}</div><div class="fare-caption">{note}</div></div>')


svg_start = HERO.index("<svg ")
svg_end = HERO.index("</svg>", svg_start) + len("</svg>")
hero_svg = HERO[svg_start:svg_end]
hero_data = base64.b64encode(hero_svg.encode("utf-8")).decode("ascii")
hero_html = HERO[:svg_start] + '<div class="hero-art" aria-hidden="true"></div>' + HERO[svg_end:]
st.html(CSS + f'<style>.hero-art{{background-image:url("data:image/svg+xml;base64,{hero_data}");}}</style>')
st.html(hero_html)
left, right = st.columns([1, 1.12], gap="large")
now = datetime.now(NY)
with left:
    with st.container(key="trip_panel"):
        panel_header("01 / Votre course", "Où allons-nous ?", "Sélectionnez vos lieux ou renseignez leurs coordonnées GPS.")
        start = select_place("Départ", "Empire State Building", "pickup")
        end = select_place("Arrivée", "Central Park · Metropolitan Museum", "dropoff")
        st.divider()
        date_col, time_col = st.columns(2)
        date = date_col.date_input("Date de départ", value=now.date(), format="DD/MM/YYYY")
        time = time_col.time_input("Heure de départ (NY)", value=now.time().replace(second=0, microsecond=0), step=60)
        passengers = st.slider("Nombre de passagers", min_value=1, max_value=6, value=1)
        st.caption("Heure locale de New York · conversion automatique en UTC.")
        submitted = st.button("Estimer mon tarif  →", type="primary", use_container_width=True)
        signature = (start, end, date, time, passengers)
        if submitted:
            st.session_state.pop("nyc_result", None)
            if start == end:
                st.warning("Choisissez deux lieux différents.")
            else:
                try:
                    utc_time = pickup_utc(date, time)
                except ValueError as exc:
                    st.warning(str(exc))
                else:
                    params = {"pickup_datetime": utc_time, "pickup_latitude": start[0], "pickup_longitude": start[1], "dropoff_latitude": end[0], "dropoff_longitude": end[1], "passenger_count": passengers}
                    try:
                        with st.spinner("Calcul du tarif…"):
                            fare = get_fare(params)
                        st.session_state["nyc_result"] = (signature, fare)
                    except (requests.RequestException, ValueError, KeyError, TypeError, FileNotFoundError):
                        st.error("Le tarif n’a pas pu être calculé. Vérifiez la configuration de l’API ou réessayez dans quelques instants.")
with right:
    with st.container(key="map_panel"):
        panel_header("02 / New York City", "Votre trajet sur la carte", "Survolez New York et zoomez sur ses bâtiments.")
        draw_map(start, end)
        stored = st.session_state.get("nyc_result")
        show_result(stored[1] if stored and stored[0] == signature else None)
