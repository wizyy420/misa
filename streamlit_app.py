import streamlit as st
from openai import OpenAI
import base64

st.set_page_config(page_title="Hacking Buddy", page_icon="🔐")

# Klient łączy się z darmowym API Hugging Face (Inference Providers)
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=st.secrets["HF_TOKEN"],  # ustawiamy w Secrets na Streamlit Cloud
)

# Model z obsługą obrazów (rozumie screenshoty), darmowy w ramach limitu
MODEL = "Qwen/Qwen2-VL-7B-Instruct"

SYSTEM_PROMPT = """Jesteś przyjaznym, cierpliwym nauczycielem cyberbezpieczeństwa i pentestingu.
Rozmawiasz z kimś, kto zaczyna kompletnie od zera - nie zna się na sieciach, Linuksie ani hackingu.

Zasady:
- Tłumacz WSZYSTKO prostym językiem, jakbyś tłumaczył koledze bez żadnego backgroundu technicznego.
- Unikaj żargonu bez natychmiastowego wyjaśnienia go prostymi słowami/analogiami.
- Tematy które znasz dobrze: sieci komputerowe (IP, porty, HTTP), Linux, VirtualBox/VM,
  OWASP Top 10 (błędy jak SQL injection, XSS, path traversal, security misconfiguration),
  znajdowanie wrażliwych/ukrytych plików na stronach, narzędzia (nmap, Burp Suite, gobuster, curl),
  bug bounty i legalne platformy do ćwiczenia (PortSwigger Web Security Academy, TryHackMe, HackTheBox).
- Gdy dostajesz screenshot błędu (np. z terminala, VirtualBox, przeglądarki) - przeanalizuj go dokładnie,
  wytłumacz co dokładnie oznacza komunikat, i zaproponuj konkretne kolejne kroki.
- Zawsze delikatnie przypominaj o legalności: testowanie i łamanie rzeczy tylko na własnych labach
  (VM, Juice Shop, PortSwigger) albo w ramach autoryzowanych programów bug bounty z jasnym zakresem.
- Bądź konkretny i praktyczny, nie lej wody. Krótkie, jasne odpowiedzi zamiast ścian tekstu."""

st.title("🔐 Hacking Buddy")
st.caption("Twój tłumacz cyberbezpieczeństwa - pytaj śmiało, wklej screenshot błędu jeśli trzeba.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Wyświetl dotychczasową rozmowę
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        for part in msg["content"]:
            if part["type"] == "text":
                st.markdown(part["text"])
            elif part["type"] == "image_url":
                st.image(part["image_url"]["url"])

uploaded_image = st.file_uploader(
    "Dołącz screenshot błędu (opcjonalnie)", type=["png", "jpg", "jpeg"]
)
prompt = st.chat_input("Zadaj pytanie o hacking, sieci, VM...")

if prompt:
    content = [{"type": "text", "text": prompt}]
    if uploaded_image:
        b64 = base64.b64encode(uploaded_image.getvalue()).decode("utf-8")
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{b64}"},
        })

    st.session_state.messages.append({"role": "user", "content": content})
    with st.chat_message("user"):
        st.markdown(prompt)
        if uploaded_image:
            st.image(uploaded_image)

    api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in st.session_state.messages:
        api_messages.append({"role": msg["role"], "content": msg["content"]})

    with st.chat_message("assistant"):
        with st.spinner("Myślę..."):
            response = client.chat.completions.create(
                model=MODEL,
                messages=api_messages,
                max_tokens=800,
            )
            answer = response.choices[0].message.content
            st.markdown(answer)

    st.session_state.messages.append(
        {"role": "assistant", "content": [{"type": "text", "text": answer}]}
    )
