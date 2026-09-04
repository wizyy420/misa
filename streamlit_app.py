import streamlit as st
from groq import Groq

# Konfiguracja
client = Groq(api_key=st.secrets["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"])

# Definiowanie osobowości
PERSONALITIES = {
    "haker": "Jesteś doświadczonym hakerem, który pracował jako etyczny haker. Wyjaśniasz zagadnienia bezpieczeństwa w sposób przystępny, ale dokładny. Zawsze podkreślasz kolejność działań i ostrzegasz gdy jakieś działania mogą spowodować problemy prawne.",
    "Mentor SI": "Jesteś cierpliwym mentorem. Wyjaśniasz wszystko krok po kroku, jakbyś uczył początkującego. Używasz prostych analogii i przykładów.",
    "Ekspert Bezpieczeństwa": "Mówisz konkretnie, profesjonalnie. Używasz specjalistycznej terminologii. Skupiasz się na praktycznych aspektach zabezpieczeń i ich słabościach."
}

# Interfejs
st.title("Misa v2")

personality = st.selectbox("Wybierz osobowość:", list(PERSONALITIES.keys()))
user_input = st.text_area("Twoje pytanie:")

if st.button("Wyślij") and user_input:
    messages = [
        {"role": "system", "content": PERSONALITIES[personality]},
        {"role": "user", "content": user_input}
    ]
    
    response = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=messages,
        max_tokens=1000,
        temperature=0.7  # Kontroluje kreatywność
    )
    
    st.write(response.choices[0].message.content)
