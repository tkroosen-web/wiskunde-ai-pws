import streamlit as st
import groq
import os
import re
import json
from datetime import datetime
import pandas as pd
import altair as alt


# ============================================================
# WISKUNDE-AI — VWO 5 | GETAL & RUIMTE H9 KANSBEREKENING
# ============================================================
# Ontworpen als een zelfstandige AI-leeromgeving:
# - Leerlingomgeving met drie begeleidingsmodi
# - Lokale Ollama/Llama-AI
# - Kennisbasis uit boek_tekst.txt + boek_opdrachten.txt
# - Docentdashboard
# - Klassenbeheer
# - Lokale chatgeschiedenis
# - Volledige scheiding tussen leerling- en docentpagina
# ============================================================


# =========================
# 1. BASISCONFIGURATIE
# =========================

st.set_page_config(
    page_title="Wiskunde-AI | VWO 5 H9",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

MODEL = "llama3.1"
CHAPTER = "VWO 5 · H9 Kansberekening"

MODI = {
    "Direct antwoord": "direct",
    "Antwoord + uitleg": "uitleg",
    "Docent-modus": "docent",
}

MODE_LABELS = {
    "direct": "Direct antwoord",
    "uitleg": "Antwoord + uitleg",
    "docent": "Docent-modus",
}


# =========================
# 2. GLOBALE CSS
# =========================

st.markdown(
    """
<style>
/* ---------- Algemene layout ---------- */
.block-container {
    max-width: 1180px;
    padding-top: 2.8rem;
    padding-bottom: 7rem;
}

[data-testid="stSidebar"] {
    border-right: 1px solid #E2E8F0;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.8rem;
}

/* ---------- Header ---------- */
.ai-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 8px;
}

.ai-logo {
    width: 42px;
    height: 42px;
    border-radius: 12px;
    background: #2563EB;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    box-shadow: 0 4px 12px rgba(37,99,235,.20);
}

.ai-title {
    font-size: 28px;
    font-weight: 800;
    color: #0F172A;
    line-height: 1.1;
}

.ai-subtitle {
    color: #64748B;
    font-size: 13px;
    margin-top: 3px;
}

/* ---------- Welkomstkaart ---------- */
.welcome-card {
    border: 1px solid #E2E8F0;
    background: #F8FAFC;
    border-radius: 18px;
    padding: 24px;
    margin: 10px 0 20px 0;
}

.welcome-title {
    font-size: 22px;
    font-weight: 750;
    color: #0F172A;
    margin-bottom: 5px;
}

.welcome-text {
    color: #64748B;
    line-height: 1.55;
}

/* ---------- Chat ---------- */
.chat-user {
    background: #2563EB;
    color: white;
    padding: 13px 17px;
    border-radius: 16px 16px 4px 16px;
    margin: 8px 0 8px auto;
    max-width: 82%;
}

.chat-ai {
    background: #F8FAFC;
    color: #1E293B;
    padding: 15px 18px;
    border: 1px solid #E2E8F0;
    border-left: 4px solid #2563EB;
    border-radius: 4px 16px 16px 16px;
    margin: 8px auto 8px 0;
    max-width: 88%;
}

/* ---------- Info/feature kaarten ---------- */
.feature-card {
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 15px;
    background: white;
    min-height: 105px;
}

.feature-title {
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 5px;
}

.feature-text {
    color: #64748B;
    font-size: 13px;
    line-height: 1.45;
}

/* ---------- Dashboard ---------- */
.dashboard-header {
    padding: 22px;
    border: 1px solid #E2E8F0;
    border-radius: 18px;
    background: linear-gradient(135deg, #F8FAFC 0%, #FFFFFF 100%);
    margin-bottom: 18px;
}

.kpi-note {
    color: #64748B;
    font-size: 12px;
    margin-top: -8px;
}

/* ---------- Kleine labels ---------- */
.mode-badge {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 999px;
    background: #EFF6FF;
    color: #1D4ED8;
    font-size: 12px;
    font-weight: 700;
}

.source-badge {
    display: inline-block;
    padding: 4px 8px;
    border-radius: 999px;
    background: #F1F5F9;
    color: #475569;
    font-size: 11px;
}

/* ---------- Startscherm moduskeuze ---------- */
.mode-choice-heading {
    margin: 18px 0 12px 0;
}
.mode-choice-heading strong {
    color: #0F172A;
    font-size: 17px;
}
.mode-choice-heading span {
    color: #64748B;
    font-size: 13px;
}
.mode-description {
    color: #64748B;
    font-size: 12px;
    line-height: 1.4;
    text-align: center;
    min-height: 38px;
    margin-top: 4px;
}
/* Geselecteerde modus krijgt een blauwe rand */
.st-key-start_mode_direct button,
.st-key-start_mode_uitleg button,
.st-key-start_mode_docent button {
    min-height: 64px;
    border-radius: 14px;
    font-weight: 700;
    background: #F8FAFC;
    color: #0F172A;
    border: 1px solid #E2E8F0;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
}
.st-key-start_mode_direct button:hover,
.st-key-start_mode_uitleg button:hover,
.st-key-start_mode_docent button:hover {
    border-color: #93C5FD;
    color: #1D4ED8;
}
.st-key-selected_direct button,
.st-key-selected_uitleg button,
.st-key-selected_docent button {
    border: 2px solid #2563EB !important;
    color: #1D4ED8 !important;
    background: #EFF6FF !important;
}


/* Alleen de geselecteerde modus krijgt een blauwe rand */
.st-key-start_mode_direct button[data-testid="stBaseButton-primary"],
.st-key-start_mode_uitleg button[data-testid="stBaseButton-primary"],
.st-key-start_mode_docent button[data-testid="stBaseButton-primary"] {
    background: #FFFFFF !important;
    color: #1D4ED8 !important;
    border: 2px solid #2563EB !important;
    box-shadow: 0 0 0 1px rgba(37, 99, 235, 0.08) !important;
}


/* ---------- Mobiel ---------- */
@media (max-width: 700px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .chat-user, .chat-ai {
        max-width: 96%;
    }

    .ai-title {
        font-size: 23px;
    }
}
</style>
""",
    unsafe_allow_html=True,
)


# =========================
# 3. SESSION STATE
# =========================

def init_state():
    defaults = {
        "ingelogde_gebruiker": None,
        "actieve_pagina": "Leerling",
        "gebruikers_db": {
            "docent@school.nl": {
                "naam": "Docent",
                "wachtwoord": "demo123",
                "rol": "Docent",
                "klas": "V5A",
            },
            "daan@school.nl": {
                "naam": "Daan",
                "wachtwoord": "wiskunde1",
                "rol": "Leerling",
                "klas": "V5A",
            },
        },
        "klassen_instellingen": {
            "V5A": {"geblokkeerde_modus": None}
        },
        "messages": [],
        "chat_geschiedenis": {},
        "gezochte_sommen": [],
        "sommen_opgelost": 0,
        "huidige_opdracht_nummer": "Onbekend",
        "huidige_methode": "",
        "huidige_ai_output": "",
        "hint_level": 1,
        "fout_bekeken": False,
        "huidige_som_afgerond": False,
        "gekozen_modus": "3. Docent-modus (Alleen tips)",
        "feedback": [],
        "analytics_events": [],
        "chat_loaded_for_user": None,
        "show_sources": True,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()


# =========================
# 4. HULPFUNCTIES
# =========================

def veilige_bestandsnaam(email):
    if not email:
        return "gast"
    return email.replace("@", "_").replace(".", "_")


def chatbestand():
    return f"chats_{veilige_bestandsnaam(st.session_state.ingelogde_gebruiker)}.json"


def sla_chatgeschiedenis_op():
    try:
        with open(chatbestand(), "w", encoding="utf-8") as f:
            json.dump(
                st.session_state.chat_geschiedenis,
                f,
                ensure_ascii=False,
                indent=2,
            )
    except Exception:
        pass


def laad_chatgeschiedenis():
    bestand = chatbestand()

    if not os.path.exists(bestand):
        st.session_state.chat_geschiedenis = {}
        st.session_state.chat_loaded_for_user = st.session_state.ingelogde_gebruiker
        return

    try:
        with open(bestand, "r", encoding="utf-8") as f:
            data = json.load(f)

        st.session_state.chat_geschiedenis = data if isinstance(data, dict) else {}
    except Exception:
        st.session_state.chat_geschiedenis = {}

    st.session_state.chat_loaded_for_user = st.session_state.ingelogde_gebruiker


def reset_huidige_chat():
    st.session_state.messages = []
    st.session_state.huidige_opdracht_nummer = "Onbekend"
    st.session_state.huidige_methode = ""
    st.session_state.huidige_ai_output = ""
    st.session_state.hint_level = 1
    st.session_state.fout_bekeken = False
    st.session_state.huidige_som_afgerond = False


def sla_huidige_chat_op():
    if not st.session_state.messages:
        return

    nummer = st.session_state.get("huidige_opdracht_nummer", "Onbekend")
    if nummer == "Onbekend":
        return

    st.session_state.chat_geschiedenis[f"Opdracht {nummer}"] = list(
        st.session_state.messages
    )
    sla_chatgeschiedenis_op()


def log_event(event_type, **extra):
    event = {
        "tijd": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "gebruiker": st.session_state.ingelogde_gebruiker,
        "klas": st.session_state.get("user_klas", ""),
        "event": event_type,
    }
    event.update(extra)
    st.session_state.analytics_events.append(event)


def huidige_user():
    return st.session_state.gebruikers_db[st.session_state.ingelogde_gebruiker]


def extract_opdracht_nummer(prompt):
    nummers = re.findall(r"\d+", prompt)
    return nummers[0] if nummers else None


def render_ai_markdown(content):
    """Render AI-LaTeX in een vorm die Streamlit Markdown correct weergeeft."""
    if not content:
        return

    content = re.sub(r"\\\[(.*?)\\\]", r"$$\1$$", content, flags=re.DOTALL)
    content = re.sub(r"\\\((.*?)\\\)", r"$\1$", content, flags=re.DOTALL)

    st.markdown(content)


def zoek_opdracht_blok(full_text, nummer):
    if not full_text or not nummer:
        return ""

    # Eerst de normale structuur "Opdracht 36" proberen.
    patroon = rf"Opdracht\s*{re.escape(str(nummer))}\b"
    match = re.search(patroon, full_text, flags=re.IGNORECASE)

    if match:
        start = match.start()
        volgende = re.search(
            r"Opdracht\s*\d+\b",
            full_text[match.end():],
            flags=re.IGNORECASE,
        )

        if volgende:
            end = match.end() + volgende.start()
            return full_text[start:end].strip()

        return full_text[start:].strip()

    # Fallback voor de oude extractiestructuur.
    blokken = re.split(r"Opdracht", full_text, flags=re.IGNORECASE)
    for blok in blokken:
        if blok.strip().startswith(str(nummer)):
            return "Opdracht " + blok.strip()

    return ""


def herken_methode(vraag, uitwerking):
    tekst = f"{vraag}\n{uitwerking}".lower()

    if (
        "zonder terugleggen" in tekst
        or "hypergeometr" in tekst
        or "steekproef zonder teruglegging" in tekst
    ):
        return (
            "Hypergeometrische verdeling",
            "De opgave wijst op trekken zonder terugleggen uit een vaste populatie."
        )

    if (
        "normale verdeling" in tekst
        or "normaal verdeeld" in tekst
        or "normalcdf" in tekst
        or "gemiddelde" in tekst and "standaardafwijking" in tekst
    ):
        return (
            "Normale verdeling",
            "De opgave gebruikt kenmerken van een continue, normaal verdeelde variabele."
        )

    if (
        "binomiale verdeling" in tekst
        or "binomcdf" in tekst
        or "binompdf" in tekst
        or "met terugleggen" in tekst
    ):
        return (
            "Binomiale verdeling",
            "De opgave past bij herhaalde pogingen met twee uitkomsten en een vaste kans."
        )

    return (
        "Nog niet zeker",
        "Ik heb in de beschikbare opgave geen betrouwbaar signaal gevonden om de methode automatisch vast te leggen."
    )


def maak_foutcheck(prompt):
    fout_p = re.findall(r"p\s*=\s*([1-9]\d+)", prompt.lower())
    if fout_p:
        return (
            f"Je typte `p = {fout_p[0]}`. Een kans p ligt tussen 0 en 1. "
            f"Controleer of je bijvoorbeeld `0.{fout_p[0]}` bedoelde."
        )
    return None


# =========================
# 5. KENNISBASIS
# =========================

@st.cache_resource
def laad_wiskunde_data():
    from langchain_core.documents import Document

    uitwerkingen = ""
    opdrachten = ""

    if os.path.exists("boek_tekst.txt"):
        with open("boek_tekst.txt", "r", encoding="utf-8") as f:
            uitwerkingen = f.read()

    if os.path.exists("boek_opdrachten.txt"):
        with open("boek_opdrachten.txt", "r", encoding="utf-8") as f:
            opdrachten = f.read()

    return {
        "uitwerkingen": Document(page_content=uitwerkingen),
        "opdrachten": Document(page_content=opdrachten),
    }


try:
    wiskunde_data = laad_wiskunde_data()
except Exception as e:
    wiskunde_data = {
        "uitwerkingen": type("DocumentFallback", (), {"page_content": ""})(),
        "opdrachten": type("DocumentFallback", (), {"page_content": ""})(),
    }
    st.error(f"De kennisbasis kon niet worden geladen: {e}")


def haal_opdracht_context(prompt):
    nummer = extract_opdracht_nummer(prompt)

    if not nummer:
        return {
            "nummer": "Onbekend",
            "vraag": "",
            "uitwerking": "",
            "bron": "Geen opdrachtnummer herkend",
        }

    vraag = zoek_opdracht_blok(
        wiskunde_data["opdrachten"].page_content,
        nummer,
    )
    uitwerking = zoek_opdracht_blok(
        wiskunde_data["uitwerkingen"].page_content,
        nummer,
    )

    bron = "Kennisbasis hoofdstuk 9"
    if not vraag and not uitwerking:
        bron = "Geen exacte opdracht gevonden"

    return {
        "nummer": nummer,
        "vraag": vraag,
        "uitwerking": uitwerking,
        "bron": bron,
    }


# =========================
# 6. AI-PROMPTS
# =========================

def bouw_instructie(prompt, context, modus):
    vraag = context["vraag"]
    uitwerking = context["uitwerking"]
    methode, reden = herken_methode(vraag, uitwerking)

    st.session_state.huidige_methode = methode

    basis = f"""
Je bent Wiskunde-AI, een rustige en betrouwbare tutor voor VWO 5 Wiskunde A.
Het onderwerp is Getal & Ruimte, hoofdstuk 9: Kansberekening.
Je communiceert uitsluitend in duidelijk Nederlands.

BELANGRIJKE REGELS:
- Gebruik de meegeleverde broncontext als belangrijkste bron.
- Verzin geen ontbrekende gegevens uit de bron.
- Als de exacte opdracht niet in de context staat, zeg dat eerlijk.
- Controleer je wiskundige redenering voordat je antwoord geeft.
- Gebruik Nederlandse wiskundetaal op VWO 5-niveau.
- Geef geen informatie over andere hoofdstukken als dat niet nodig is.
- Maak duidelijk onderscheid tussen gegevens, berekening en conclusie.
- Gebruik Markdown voor formules en overzichtelijke stappen.
- Als een methodeherkenning hieronder "Nog niet zeker" is, doe dan zelf eerst een inhoudelijke controle.

AUTOMATISCHE METHODE-INDICATIE:
Methode: {methode}
Reden: {reden}

VRAAG VAN DE LEERLING:
{prompt}

EXACTE VRAAG UIT DE KENNISBASIS:
{vraag if vraag else "[Niet gevonden]"}

UITWERKING UIT DE KENNISBASIS:
{uitwerking if uitwerking else "[Niet gevonden]"}
"""

    if modus == "direct":
        return basis + """
MODUS: DIRECT ANTWOORD

Geef een direct en duidelijk antwoord.
Geef waar nodig de noodzakelijke berekening, maar houd de uitleg compact.
Als de bron een exacte uitwerking bevat, controleer die en gebruik die als basis.
Sluit af met een duidelijk eindantwoord.
"""

    if modus == "uitleg":
        return basis + """
MODUS: ANTWOORD + UITLEG

Werk als een persoonlijke tutor.
Gebruik bij voorkeur deze structuur:

### Methode
Welke kansverdeling/methode wordt gebruikt en waarom?

### Gegevens
Welke gegevens zijn gegeven?

### Berekening
Laat de relevante formule en/of GR-notatie zien.

### Antwoord
Geef het eindantwoord en een korte controle of interpretatie.

Leg moeilijke begrippen eenvoudig uit, passend bij VWO 5.
"""

    return basis + """
MODUS: DOCENT-MODUS

Je mag het eindantwoord niet verklappen zolang de leerling nog zelfstandig kan nadenken.
Geef maximaal drie oplopende hints:

### Hint 1 — Denk aan de methode
Help de leerling herkennen welke methode en gegevens nodig zijn.

### Hint 2 — Denk aan de berekening
Geef aan welke formule, kansverdeling of GR-functie nodig is.

### Hint 3 — Zet de stap
Geef de eerstvolgende concrete denkrichting, maar niet het eindantwoord.

Gebruik geen eindantwoord uit de uitwerking.
Geef ook geen complete berekening voor de leerling.
"""


def vraag_aan_ollama(prompt, context, modus):
    
    instructie = bouw_instructie(prompt, context, modus)
    
    # 🔐 VEILIGE ONLINE SLEUTEL (We koppelen hem straks live in de Streamlit Cloud!)
    # Als je hem lokaal wilt testen, kun je tijdelijk je gsk_... sleutel hieronder tussen de aanhalingstekens plakken.
    api_sleutel = st.secrets.get("GROQ_API_KEY", "")
    
    if not api_sleutel:
        return "Fout: De online AI-sleutel (GROQ_API_KEY) is nog niet geconfigureerd in de Streamlit Cloud instellingen."

    try:
        client = groq.Groq(api_key=api_sleutel)
        
        # We gebruiken een actueel production-model van Groq: OpenAI GPT-OSS 20B.
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": "Je bent een betrouwbare online wiskundetutor voor VWO 5. Je antwoordt uitsluitend in het Nederlands, brongebonden, controleerbaar en didactisch."
                },
                {
                    "role": "user",
                    "content": instructie
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Er ging iets mis bij het bereiken van de online AI-tutor: {e}"



# =========================
# 7. LOGIN
# =========================

if st.session_state.ingelogde_gebruiker is None:
    left, center, right = st.columns([1, 1.4, 1])

    with center:
        st.markdown("<br><br>", unsafe_allow_html=True)

        st.markdown(
            """
            <div style="text-align:center;">
                <div style="font-size:42px;">🎓</div>
                <h1 style="margin:0;color:#0F172A;">Wiskunde-AI</h1>
                <p style="color:#64748B;">
                    Persoonlijke AI-tutor voor VWO 5 · H9 Kansberekening
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        login_tab, register_tab = st.tabs(["Inloggen", "Account aanmaken"])

        with login_tab:
            email = st.text_input(
                "E-mailadres",
                placeholder="bijv. daan@school.nl",
                key="login_email",
            )
            wachtwoord = st.text_input(
                "Wachtwoord",
                type="password",
                key="login_password",
            )

            if st.button(
                "Inloggen",
                type="primary",
                use_container_width=True,
                key="login_btn",
            ):
                if (
                    email in st.session_state.gebruikers_db
                    and st.session_state.gebruikers_db[email]["wachtwoord"]
                    == wachtwoord
                ):
                    st.session_state.ingelogde_gebruiker = email
                    st.session_state.actieve_pagina = "Leerling"
                    laad_chatgeschiedenis()
                    st.rerun()
                else:
                    st.error("E-mailadres of wachtwoord is onjuist.")

        with register_tab:
            naam = st.text_input("Voornaam", key="reg_name")
            reg_email = st.text_input("E-mailadres", key="reg_email")
            reg_ww = st.text_input(
                "Wachtwoord",
                type="password",
                key="reg_password",
            )
            rol = st.selectbox(
                "Ik ben een",
                ["Leerling", "Docent"],
                key="reg_role",
            )
            klas = st.text_input(
                "Klas",
                placeholder="bijv. V5A",
                key="reg_class",
            ).upper()

            if st.button(
                "Account aanmaken",
                use_container_width=True,
                key="register_btn",
            ):
                if not all([naam, reg_email, reg_ww, klas]):
                    st.warning("Vul alle velden in.")
                elif reg_email in st.session_state.gebruikers_db:
                    st.error("Dit e-mailadres bestaat al.")
                else:
                    st.session_state.gebruikers_db[reg_email] = {
                        "naam": naam,
                        "wachtwoord": reg_ww,
                        "rol": rol,
                        "klas": klas,
                    }

                    if klas not in st.session_state.klassen_instellingen:
                        st.session_state.klassen_instellingen[klas] = {
                            "geblokkeerde_modus": None
                        }

                    st.success(
                        "Account aangemaakt. Je kunt nu inloggen."
                    )

    st.stop()


# =========================
# 8. USER INFO
# =========================

user_info = huidige_user()
user_naam = user_info.get(
    "naam",
    st.session_state.ingelogde_gebruiker.split("@")[0].capitalize(),
)
user_rol = user_info.get("rol", "Leerling")
user_klas = user_info.get("klas", "V5A")

st.session_state.user_klas = user_klas

if st.session_state.chat_loaded_for_user != st.session_state.ingelogde_gebruiker:
    laad_chatgeschiedenis()


# =========================
# 9. SIDEBAR — ALTIJD BESCHIKBAAR
# =========================

with st.sidebar:
    st.markdown(
        """
        <div class="ai-brand">
            <div class="ai-logo">🎓</div>
            <div>
                <div class="ai-title" style="font-size:20px;">Wiskunde-AI</div>
                <div class="ai-subtitle">VWO 5 · H9 Kansberekening</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    if st.button(
        "＋ Nieuw gesprek",
        use_container_width=True,
        key="sidebar_new_chat",
    ):
        sla_huidige_chat_op()
        reset_huidige_chat()
        st.session_state.actieve_pagina = "Leerling"
        st.rerun()

    if user_rol == "Docent":
        st.markdown("#### Navigatie")
        if st.button(
            "Leerlingomgeving",
            use_container_width=True,
            key="nav_student",
        ):
            st.session_state.actieve_pagina = "Leerling"
            st.rerun()

        if st.button(
            "Docentdashboard",
            use_container_width=True,
            key="nav_teacher",
        ):
            st.session_state.actieve_pagina = "Docent"
            st.rerun()

        if st.button(
            "Klassenbeheer",
            use_container_width=True,
            key="nav_classes",
        ):
            st.session_state.actieve_pagina = "Klassenbeheer"
            st.rerun()

    else:
        st.session_state.actieve_pagina = "Leerling"

    # De begeleidingsmodus wordt nu uitsluitend in het startscherm gekozen.

        st.markdown("#### Recente opdrachten")

        if not st.session_state.chat_geschiedenis:
            st.caption("Nog geen opgeslagen gesprekken.")
        else:
            # Laat maximaal 8 recente gesprekken zien.
            items = list(
                st.session_state.chat_geschiedenis.items()
            )[-8:]

            for naam, berichten in reversed(items):
                if st.button(
                    naam,
                    use_container_width=True,
                    key=f"history_{naam}",
                ):
                    st.session_state.messages = list(berichten)
                    match = re.search(r"\d+", naam)
                    st.session_state.huidige_opdracht_nummer = (
                        match.group(0) if match else "Onbekend"
                    )
                    st.session_state.hint_level = 1
                    st.session_state.actieve_pagina = "Leerling"
                    st.rerun()

        st.divider()

        with st.expander("Instellingen"):
            st.session_state.gr_type = st.selectbox(
                "Grafische rekenmachine",
                [
                    "Texas Instruments (TI-84)",
                    "Casio (Fx-CG50)",
                    "NumWorks",
                ],
                key="gr_selector",
            )

    # Profiel onderaan.
    st.divider()
    letter = user_naam[0].upper() if user_naam else "?"

    st.markdown(
        f"""
        <div style="display:flex;align-items:center;gap:10px;">
            <div style="
                width:38px;height:50px;border-radius:50%;
                background:#2563EB;color:white;
                display:flex;align-items:center;justify-content:center;
                font-weight:700;">
                {letter}
            </div>
            <div>
                <b style="color:#0F172A;">{user_naam}</b><br>
                <span style="font-size:12px;color:#64748B;">
                    {user_rol} · {user_klas}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "Uitloggen",
        use_container_width=True,
        key="logout",
    ):
        sla_huidige_chat_op()
        st.session_state.ingelogde_gebruiker = None
        st.session_state.chat_loaded_for_user = None
        st.session_state.actieve_pagina = "Leerling"
        st.rerun()


# ============================================================
# 10. PAGINA 1 — LEERLING
# ============================================================

if st.session_state.actieve_pagina == "Leerling":

    st.markdown(
        """
        <div class="ai-brand">
            <div class="ai-logo">🤖</div>
            <div>
                <div class="ai-title">Wiskunde-AI</div>
                <div class="ai-subtitle">
                    Persoonlijke tutor voor Getal & Ruimte · VWO 5 · H9
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---------- Welkomstscherm ----------
    if not st.session_state.messages:
        st.markdown(
            f"""
            <div class="welcome-card">
                <div class="welcome-title">Hoi {user_naam}! 👋</div>
                <div class="welcome-text">
                    Ik help je met <b>hoofdstuk 9 Kansberekening</b>.
                    Kies hieronder hoe je wilt dat ik je help.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            "<div class='mode-choice-heading'><strong>Hoe wil je hulp krijgen?</strong><br><span>Kies een modus voor dit gesprek.</span></div>",
            unsafe_allow_html=True,
        )

        current_mode = st.session_state.get("gekozen_modus_code", "docent")
        mode_data = [
            ("direct", "⚡ Direct antwoord", "Voor als je snel wilt controleren wat het antwoord is."),
            ("uitleg", "📚 Antwoord + uitleg", "Voor een volledige uitleg van methode, gegevens en berekening."),
            ("docent", "👨‍🏫 Docent-modus", "De AI geeft alleen oplopende hints, zodat je zelf blijft rekenen."),
        ]
        cols = st.columns(3, gap="small")
        for col, (code, title, description) in zip(cols, mode_data):
            with col:
                key = f"start_mode_{code}"
                if st.button(title, key=key, use_container_width=True, type="primary" if current_mode == code else "secondary"):
                    st.session_state.gekozen_modus_code = code
                    st.rerun()
                if current_mode == code:
                    st.markdown(f"<div class='mode-description'><b style='color:#2563EB;'>✓ Gekozen</b><br>{description}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='mode-description'>{description}</div>", unsafe_allow_html=True)

    # ---------- Chatgeschiedenis ----------
    for message in st.session_state.messages:
        role = message.get("role", "assistant")
        content = message.get("content", "")

        if role == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(content)
        else:
            with st.chat_message("assistant", avatar="🤖"):
                render_ai_markdown(content)
                st.caption("⚠️ AI kan fouten maken. Controleer belangrijke berekeningen altijd.")

    # ---------- Huidige begeleidingsmodus + chatbalk ----------
    # De chatbalk staat bewust buiten kolommen, zodat Streamlit hem
    # op de normale vaste plek onderaan het scherm kan plaatsen.
    afgedwongen_modus = st.session_state.klassen_instellingen.get(
        user_klas, {}
    ).get("geblokkeerde_modus")

    if afgedwongen_modus:
        modus_code = afgedwongen_modus
    else:
        modus_code = st.session_state.get("gekozen_modus_code", "docent")

    st.markdown(
        f"<div style='margin:8px 0 4px 0;'><span class='mode-badge'>{MODE_LABELS.get(modus_code, modus_code)}</span></div>",
        unsafe_allow_html=True,
    )

    prompt = st.chat_input("Stel je vraag over H9 Kansberekening…")

    if prompt:
        st.session_state.messages.append(
            {"role": "user", "content": prompt}
        )

        context = haal_opdracht_context(prompt)
        nummer = context["nummer"]

        if nummer != "Onbekend":
            st.session_state.huidige_opdracht_nummer = nummer

            if f"Opdracht {nummer}" not in st.session_state.gezochte_sommen:
                st.session_state.gezochte_sommen.append(
                    f"Opdracht {nummer}"
                )

        # Gekozen modus.
        afgedwongen = st.session_state.klassen_instellingen.get(
            user_klas, {}
        ).get("geblokkeerde_modus")

        if afgedwongen:
            modus = afgedwongen
        else:
            modus = st.session_state.get(
                "gekozen_modus_code",
                "docent",
            )

        log_event(
            "vraag",
            opdracht=nummer,
            modus=MODE_LABELS.get(modus, modus),
        )

        # Foutcontrole.
        foutmelding = maak_foutcheck(prompt)
        if foutmelding:
            with st.chat_message("assistant", avatar="⚠️"):
                st.warning(foutmelding)

        # Methodeherkenning.
        methode, reden = herken_methode(
            context["vraag"],
            context["uitwerking"],
        )
        st.session_state.huidige_methode = methode

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Ik kijk naar de opgave en denk mee…"):
                ai_output = vraag_aan_ollama(
                    prompt,
                    context,
                    modus,
                )

            render_ai_markdown(ai_output)
            st.caption("⚠️ AI kan fouten maken. Controleer belangrijke berekeningen altijd.")


        st.session_state.messages.append(
            {"role": "assistant", "content": ai_output}
        )

        st.session_state.huidige_ai_output = ai_output
        st.session_state.hint_level = 1
        st.session_state.fout_bekeken = False

        sla_huidige_chat_op()

    # ---------- Extra docentmodus ----------
    if (
        st.session_state.get("gekozen_modus_code") == "docent"
        and st.session_state.get("huidige_ai_output")
    ):
        st.divider()
        st.markdown("### 👨‍🏫 Adaptieve ondersteuning")

        raw = st.session_state.huidige_ai_output

        h1 = re.search(
            r"(?i)###\s*Hint\s*1.*?(?=###\s*Hint\s*2|$)",
            raw,
            re.DOTALL,
        )
        h2 = re.search(
            r"(?i)###\s*Hint\s*2.*?(?=###\s*Hint\s*3|$)",
            raw,
            re.DOTALL,
        )
        h3 = re.search(
            r"(?i)###\s*Hint\s*3.*",
            raw,
            re.DOTALL,
        )

        with st.container(border=True):
            st.markdown("**Hint 1 — Methode**")
            if h1:
                render_ai_markdown(
                    re.sub(
                        r"(?i)###\s*Hint\s*1\s*[—-]?\s*",
                        "",
                        h1.group(0),
                    ).strip()
                )
            else:
                st.write(
                    "Welke kansverdeling past bij de situatie? "
                    "Let vooral op met of zonder terugleggen."
                )

        if st.session_state.hint_level >= 2:
            with st.container(border=True):
                st.markdown("**Hint 2 — Berekening**")
                if h2:
                    render_ai_markdown(
                        re.sub(
                            r"(?i)###\s*Hint\s*2\s*[—-]?\s*",
                            "",
                            h2.group(0),
                        ).strip()
                    )
                else:
                    st.write(
                        "Bedenk welke formule of GR-functie bij de gevonden methode hoort."
                    )
        else:
            if st.button(
                "🔎 Hint 2 bekijken",
                use_container_width=True,
                key="hint2",
            ):
                st.session_state.hint_level = 2
                st.rerun()

        if st.session_state.hint_level >= 3:
            with st.container(border=True):
                st.markdown("**Hint 3 — Volgende stap**")
                if h3:
                    render_ai_markdown(
                        re.sub(
                            r"(?i)###\s*Hint\s*3\s*[—-]?\s*",
                            "",
                            h3.group(0),
                        ).strip()
                    )
                else:
                    st.write(
                        "Vul de gevonden gegevens in en voer de berekening zelf uit."
                    )
        elif st.session_state.hint_level == 2:
            if st.button(
                "🔎 Hint 3 bekijken",
                use_container_width=True,
                key="hint3",
            ):
                st.session_state.hint_level = 3
                st.rerun()

        if st.session_state.hint_level >= 2:
            st.markdown("---")
            if st.button(
                "🔍 Ik heb een fout gemaakt",
                use_container_width=True,
                key="mistake_help",
            ):
                st.session_state.fout_bekeken = True

        if st.session_state.fout_bekeken:
            with st.container(border=True):
                st.markdown("**Controleer vooral deze punten:**")

                methode = st.session_state.get(
                    "huidige_methode",
                    "",
                ).lower()

                if "hyper" in methode:
                    st.write(
                        "• Controleer of je inderdaad zonder terugleggen werkt."
                    )
                    st.write(
                        "• Controleer of je niet automatisch een binomiale verdeling hebt gebruikt."
                    )
                elif "normale" in methode:
                    st.write(
                        "• Controleer je gemiddelde en standaardafwijking."
                    )
                    st.write(
                        "• Controleer of je linker- en rechtergrens goed hebt ingevoerd."
                    )
                else:
                    st.write(
                        "• Controleer of n en p goed uit de tekst zijn gehaald."
                    )
                    st.write(
                        "• Controleer of je Pdf of Cdf nodig hebt."
                    )

# ============================================================
# 11. PAGINA 2 — DOCENTDASHBOARD
# ============================================================

elif st.session_state.actieve_pagina == "Docent":

    st.markdown(
        """
        <div class="dashboard-header">
            <h1 style="margin:0;color:#0F172A;">Docentdashboard</h1>
            <p style="margin:5px 0 0 0;color:#64748B;">
                Overzicht van gebruik, voortgang en veelgevraagde opdrachten.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if user_rol != "Docent":
        st.error("Deze omgeving is alleen beschikbaar voor docenten.")
        st.stop()

    # ---------- Data verzamelen ----------
    vragen = [
        e for e in st.session_state.analytics_events
        if e.get("event") == "vraag"
    ]

    opdrachten = st.session_state.gezochte_sommen

    # ---------- KPI's ----------
    k1, k2, k3, k4 = st.columns(4)

    k1.metric(
        "Vragen",
        len(vragen),
    )
    k2.metric(
        "Opdrachten gezocht",
        len(opdrachten),
    )
    k3.metric(
        "Opgaven opgelost",
        len(opdrachten),
    )
    k4.metric(
        "Chatberichten",
        len(st.session_state.messages),
    )

    st.divider()

    # ---------- Tabs binnen dashboard ----------
    dash_overzicht, dash_onderwerpen, dash_logboek = st.tabs(
        ["Overzicht", "Leerpatronen", "Logboek & export"]
    )

    with dash_overzicht:
        left, right = st.columns(2)

        with left:
            st.markdown("### Meest gezochte opdrachten")

            if opdrachten:
                df_opd = pd.DataFrame(
                    opdrachten,
                    columns=["Opdracht"],
                )

                telling = df_opd["Opdracht"].value_counts().rename("Aantal").reset_index()
                telling.columns = ["Opdracht", "Aantal"]

                chart = (
                    alt.Chart(telling)
                    .mark_bar()
                    .encode(
                        x=alt.X(
                            "Opdracht:N",
                            sort="-y",
                            axis=alt.Axis(labelAngle=0, labelLimit=180),
                        ),
                        y=alt.Y("Aantal:Q", title="Aantal"),
                        tooltip=["Opdracht:N", "Aantal:Q"],
                    )
                    .properties(height=300)
                )
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info(
                    "Zodra leerlingen opdrachten opzoeken, verschijnt hier een grafiek."
                )

        with right:
            st.markdown("### Gekozen AI-modi")

            if vragen:
                modi = [
                    v.get("modus", "Onbekend")
                    for v in vragen
                ]
                df_modus = (
                    pd.Series(modi, name="Modus")
                    .value_counts()
                    .rename("Aantal")
                    .reset_index()
                )
                df_modus.columns = ["Modus", "Aantal"]

                chart = (
                    alt.Chart(df_modus)
                    .mark_bar()
                    .encode(
                        x=alt.X(
                            "Modus:N",
                            sort="-y",
                            axis=alt.Axis(labelAngle=0, labelLimit=180),
                        ),
                        y=alt.Y("Aantal:Q", title="Aantal"),
                        tooltip=["Modus:N", "Aantal:Q"],
                    )
                    .properties(height=300)
                )
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info(
                    "Er zijn nog geen vraagmomenten geregistreerd."
                )

        st.markdown("### Actieve klasinstelling")

        lock = st.session_state.klassen_instellingen.get(
            user_klas,
            {},
        ).get("geblokkeerde_modus")

        if lock:
            st.info(
                f"Voor **{user_klas}** is momenteel "
                f"**{MODE_LABELS.get(lock, lock)}** afgedwongen."
            )
        else:
            st.success(
                f"Voor **{user_klas}** zijn alle drie de leerlingmodi beschikbaar."
            )

    with dash_onderwerpen:
        st.markdown("### Wat leerlingen vaak nodig hebben")

        if opdrachten:
            counts = pd.Series(opdrachten).value_counts()
            top = counts.head(10).reset_index()
            top.columns = ["Opdracht", "Aantal"]

            st.dataframe(
                top,
                use_container_width=True,
                hide_index=True,
            )

            st.caption(
                "Dit overzicht laat zien welke opdrachten binnen deze sessie het vaakst zijn opgezocht."
            )
        else:
            st.info(
                "Er is nog geen gebruiksdata beschikbaar."
            )

        st.markdown("### Didactische signalen")

        if st.session_state.feedback:
            positieve = len(
                [
                    x for x in st.session_state.feedback
                    if x.get("type") == "positief"
                ]
            )
            st.metric(
                "Positieve feedback",
                positieve,
            )
        else:
            st.write(
                "Nog geen feedback geregistreerd."
            )

        st.markdown(
            """
            **Handige interpretatie voor de docent:**
            - Veel zoekopdrachten bij hetzelfde nummer kunnen aangeven dat een opgave lastig is.
            - Veel gebruik van de docentmodus kan wijzen op behoefte aan stapsgewijze begeleiding.
            - De gegevens zijn bedoeld als ondersteuning van de docent en niet als automatische beoordeling.
            """
        )

    with dash_logboek:
        st.markdown("### Chathistorie")

        logregels = []

        for message in st.session_state.messages:
            role = (
                "LEERLING"
                if message.get("role") == "user"
                else "AI"
            )
            logregels.append(
                f"[{role}] {message.get('content', '')}"
            )

        logtekst = "\n\n".join(logregels)

        if logtekst:
            st.text_area(
                "Huidig gesprek",
                logtekst,
                height=300,
            )
        else:
            st.info("Het huidige gesprek bevat nog geen berichten.")

        st.download_button(
            "Download huidig gesprek (.txt)",
            data=logtekst,
            file_name="wiskunde_ai_gesprek.txt",
            mime="text/plain",
            disabled=not bool(logtekst),
            use_container_width=True,
        )

        # Analytics export.
        analytics_json = json.dumps(
            st.session_state.analytics_events,
            ensure_ascii=False,
            indent=2,
        )

        st.download_button(
            "Download analytics (.json)",
            data=analytics_json,
            file_name="wiskunde_ai_analytics.json",
            mime="application/json",
            use_container_width=True,
        )


# ============================================================
# 12. PAGINA 3 — KLASSENBEHEER
# ============================================================

elif st.session_state.actieve_pagina == "Klassenbeheer":

    if user_rol != "Docent":
        st.error("Deze omgeving is alleen beschikbaar voor docenten.")
        st.stop()

    st.title("Klassenbeheer")
    st.write(
        f"Beheer hier de AI-begeleiding voor klas **{user_klas}**."
    )

    st.divider()

    klassen = list(st.session_state.klassen_instellingen.keys())

    if user_klas not in klassen:
        klassen.append(user_klas)

    gekozen_klas = st.selectbox(
        "Kies een klas",
        klassen,
        key="beheer_klas",
    )

    huidige_lock = st.session_state.klassen_instellingen[
        gekozen_klas
    ].get("geblokkeerde_modus")

    opties = {
        "Geen restricties": None,
        "Direct antwoord": "direct",
        "Antwoord + uitleg": "uitleg",
        "Docent-modus": "docent",
    }

    huidige_naam = (
        "Geen restricties"
        if huidige_lock is None
        else MODE_LABELS.get(huidige_lock, "Geen restricties")
    )

    gekozen = st.radio(
        "Welke modus mogen leerlingen gebruiken?",
        list(opties.keys()),
        index=list(opties.keys()).index(huidige_naam),
        key="class_mode_radio",
    )

    if st.button(
        "Instelling opslaan",
        type="primary",
        use_container_width=True,
        key="save_class_mode",
    ):
        st.session_state.klassen_instellingen[
            gekozen_klas
        ]["geblokkeerde_modus"] = opties[gekozen]

        st.success(
            f"Instelling voor {gekozen_klas} opgeslagen."
        )
        st.rerun()

    st.divider()

    st.markdown("### Wat betekenen de modi?")

    info1, info2, info3 = st.columns(3)

    with info1:
        st.markdown(
            """
            **Direct antwoord**

            Geschikt voor leerlingen die vooral hun antwoord willen controleren.
            """
        )

    with info2:
        st.markdown(
            """
            **Antwoord + uitleg**

            Geschikt wanneer de leerling de volledige redenering wil begrijpen.
            """
        )

    with info3:
        st.markdown(
            """
            **Docent-modus**

            De AI geeft oplopende hints en probeert het zelfstandig oplossen te stimuleren.
            """
        )

    st.divider()

    st.warning(
        "Voor een echte schoolomgeving is extra toegangsbeveiliging nodig. "
        "Deze PWS-versie gebruikt een lokale demonstratie-database."
    )
