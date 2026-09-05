import streamlit as st
from groq import Groq
import requests
import json
from datetime import datetime

# Konfiguracja - pobierz klucz z sekretów Streamlit
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# Inicjalizacja klienta Groq
client = Groq(api_key=GROQ_API_KEY)

# Definiowanie osobowości z rozszerzonymi instrukcjami
PERSONALITIES = {
    "🕵️ Etyczny Haker": """Jesteś doświadczonym hakerem z 10-letnim doświadczeniem w testach penetracyjnych.
    Specjalizujesz się w:
    - Znajdowaniu podatności w aplikacjach webowych
    - Testowaniu bezpieczeństwa sieci
    - Inżynierii społecznej
    - Audytach bezpieczeństwa
    
    Zasady, których zawsze przestrzegasz:
    - Zawsze mówisz prawdę
    - Informujesz o możliwych konsekwencjach wykonania danego działania
    - Używasz prostego języka, ale podajesz konkretne przykłady
    - Zachęcasz do nauki przez praktykę na platformach (TryHackMe, HackTheBox)
    """,
    
    "👨‍🏫 Mentor Bezpieczeństwa": """Jesteś cierpliwym mentorem, który uczy początkujących podstaw ofensywy i bezpieczeństwa IT.
    Twój styl nauczania:
    - Wyjaśniasz wszystko od podstaw, bez zakładania wiedzy
    - Używasz prostych analogii z życia codziennego
    - Dzielisz złożone tematy na małe, zrozumiałe części
    - Zawsze pytasz, czy uczeń rozumie i zachęcasz do zadawania pytań
    - Podajesz praktyczne ćwiczenia do samodzielnego wykonania
    
    Specjalizujesz się w:
    - Podstawach sieci komputerowych
    - Bezpieczeństwie aplikacji webowych (OWASP Top 10)
    - Narzędziach Kali Linux
    - Podstawach kryptografii
    - Google dorking
    - Znajdowaniu możliwości testowania penetrating i hacking, bez zagrożenia dla użytkownika
    """,
    
    "🔒 Ekspert Zabezpieczeń": """Jesteś ekspertem ds. zabezpieczeń korporacyjnych z doświadczeniem w ochronie dużych systemów.
    Twoje cechy:
    - Mówisz konkretnie, profesjonalnie i rzeczowo
    - Używasz specjalistycznej terminologii, ale wyjaśniasz ją
    - Skupiasz się na praktycznych aspektach zabezpieczeń w firmach
    - Znasz najlepsze praktyki branżowe (ISO 27001, NIST, GDPR)
    - Potrafisz ocenić ryzyko i zaproponować rozwiązania
    
    Obszary Twojej wiedzy:
    - Bezpieczeństwo infrastruktury chmurowej (AWS, Azure, GCP)
    - Zarządzanie tożsamością i dostępem (IAM)
    - Bezpieczeństwo aplikacji i DevOps (DevSecOps)
    - Reagowanie na incydenty
    """,
    
    "🤖 Analityk Podatności": """Jesteś specjalistą od znajdowania i analizowania podatności.
    Twoje podejście:
    - Skupiasz się na technicznych szczegółach
    - Wyjaśniasz, jak dana podatność może być wykorzystana
    - Proponujesz konkretne sposoby naprawy
    - Znasz najnowsze CVE i trendy w bezpieczeństwie
    - Używasz narzędzi takich jak Nmap, Burp Suite, Metasploit
    
    Specjalizujesz się w:
    - Analizie skanerów podatności
    - Testach penetracyjnych
    - Audytach kodu źródłowego
    - Inżynierii reverse engineering
    - Google dorking
    - Tłumaczeniu jak krok po kroku wykonać działania
    """
}

# Rozszerzone tematy do szybkiego wyboru
QUICK_TOPICS = {
    "🔍 Pokaż mi podstawy nmap": "Pokaż mi podstawy skanowania nmap z przykładami",
    "🌐 Wyjaśnij OWASP Top 10": "Wyjaśnij OWASP Top 10 w prostych słowach z przykładami",
    "🛡️ Jak zacząć w TryHackMe": "Jak zacząć naukę na TryHackMe? Daj mi plan na pierwszy tydzień",
    "💻 Podstawy Kali Linux": "Pokaż mi podstawowe komendy Kali Linux dla początkujących",
    "🔐 Co to jest SQL Injection": "Wyjaśnij SQL Injection z przykładem i jak się przed tym bronić",
    "🌍 Jak działa VPN": "Wyjaśnij jak działa VPN i jakie ma zastosowania w bezpieczeństwie"
}

# Inicjalizacja historii rozmowy w sesji
if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_personality" not in st.session_state:
    st.session_state.current_personality = "🕵️ Etyczny Haker"

# Konfiguracja strony
st.set_page_config(
    page_title="🛡️ Asystent Bezpieczeństwa",
    page_icon="🛡️",
    layout="wide"
)

# Główny tytuł
st.title("🛡️ Asystent Bezpieczeństwa IT z Osobowościami")
st.markdown("---")

# Sidebar - konfiguracja
with st.sidebar:
    st.header("⚙️ Konfiguracja")
    
    # Wybór osobowości
    personality = st.selectbox(
        "🎭 Wybierz osobowość asystenta:",
        options=list(PERSONALITIES.keys()),
        index=list(PERSONALITIES.keys()).index(st.session_state.current_personality)
    )
    
    if personality != st.session_state.current_personality:
        st.session_state.current_personality = personality
        # Czyść historię przy zmianie osobowości
        if st.button("🗑️ Wyczyść historię rozmowy"):
            st.session_state.messages = []
            st.rerun()
    
    # Kontrola temperatury (kreatywności)
    temperature = st.slider(
        "🎨 Kreatywność (temperatura)",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Niższa wartość = bardziej precyzyjne odpowiedzi, wyższa = bardziej kreatywne"
    )
    
    # Maksymalna długość odpowiedzi
    max_tokens = st.slider(
        "📏 Długość odpowiedzi",
        min_value=200,
        max_value=3000,
        value=1100,
        step=100
    )
    
    st.markdown("---")
    st.info("💡 **Wskazówka:** Wybierz osobowość dopasowaną do Twoich potrzeb. Etyczny Haker - dla praktycznych porad, Mentor - dla nauki od podstaw, Ekspert - dla profesjonalnych analiz.")
    
    st.markdown("---")
    st.caption(f"🔄 Model: openai/gpt-oss-20b")
    st.caption(f"📊 Historią rozmowy: {len(st.session_state.messages)} wiadomości")

# Główny obszar aplikacji - dwie kolumny
col1, col2 = st.columns([2, 1])

with col1:
    # Wyświetlanie historii rozmowy
    chat_container = st.container(height=500)
    
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Input od użytkownika
    if prompt := st.chat_input("💬 Zapytaj o bezpieczeństwo, sieci, hacking..."):
        # Dodaj wiadomość użytkownika do historii
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Wyświetl wiadomość użytkownika
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generuj odpowiedź
        with st.chat_message("assistant"):
            with st.spinner("🤔 Myślę..."):
                try:
                    # Przygotuj wiadomości do API
                    messages = [
                        {"role": "system", "content": PERSONALITIES[personality]}
                    ]
                    
                    # Dodaj ostatnie 10 wiadomości dla kontekstu
                    for msg in st.session_state.messages[-10:]:
                        messages.append(msg)
                    
                    # Wywołaj API
                    response = client.chat.completions.create(
                        model="openai/gpt-oss-20b",
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=temperature
                    )
                    
                    answer = response.choices[0].message.content
                    st.markdown(answer)
                    
                    # Dodaj odpowiedź do historii
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    
                except Exception as e:
                    st.error(f"❌ Wystąpił błąd: {str(e)}")
                    st.info("💡 Spróbuj ponownie lub wybierz inny model w ustawieniach.")

with col2:
    st.subheader("⚡ Szybkie pytania")
    
    # Szybkie tematy
    for topic, question in QUICK_TOPICS.items():
        if st.button(topic, use_container_width=True):
            # Automatycznie zadaj pytanie
            st.session_state.messages.append({"role": "user", "content": question})
            
            # Generuj odpowiedź
            with st.chat_message("assistant"):
                with st.spinner("🤔 Myślę..."):
                    try:
                        messages = [
                            {"role": "system", "content": PERSONALITIES[personality]}
                        ]
                        for msg in st.session_state.messages[-10:]:
                            messages.append(msg)
                        
                        response = client.chat.completions.create(
                            model="openai/gpt-oss-20b",
                            messages=messages,
                            max_tokens=max_tokens,
                            temperature=temperature
                        )
                        
                        answer = response.choices[0].message.content
                        st.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                        
                    except Exception as e:
                        st.error(f"❌ Błąd: {str(e)}")
            
            st.rerun()
    
    st.markdown("---")
    st.subheader("📚 Przydatne linki")
    st.markdown("""
    - [TryHackMe](https://tryhackme.com/) - Nauka przez praktykę
    - [HackTheBox](https://www.hackthebox.com/) - Zaawansowane wyzwania
    - [OWASP Top 10](https://owasp.org/Top10/) - Najczęstsze podatności
    - [Exploit Database](https://www.exploit-db.com/) - Baza exploitów
    - [Kali Linux Tools](https://tools.kali.org/) - Narzędzia Kali
    """)
    
    st.markdown("---")
    if st.button("🗑️ Wyczyść całą historię", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Stopka
st.markdown("---")
st.caption("🛡️ Asystent Bezpieczeństwa IT | Wszystkie odpowiedzi są generowane przez AI i służą celom edukacyjnym.")
