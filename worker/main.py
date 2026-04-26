print("=== AGENT V2 START ===")

import os
import datetime
import random
import schedule
import time
import requests

# Modelos reales disponibles en tu cuenta OpenRouter
MODELS = [
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemma-4-31b-it:free",
    "google/gemma-4-26b-a4b-it:free",
    "openai/gpt-oss-120b:free",
    "nvidia/nemotron-3-nano-30b-a3b:free"
]

CONTENT_DIR = "/content"
API_KEY = os.getenv("OPENROUTER_API_KEY")

FALLBACK_TOPICS = [
    "mejores zapatillas para periostitis",
    "cómo ahorrar dinero en casa",
    "rutinas de entrenamiento para principiantes",
    "ideas de ingresos pasivos online",
    "comparativa hosting barato España",
]


# =========================
# 🔌 LLM CALL (robusto)
# =========================
def call_llm(prompt):
    for model in MODELS:
        print(f"[TRY] Probando modelo: {model}")

        for attempt in range(3):
            try:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "Eres un experto en SEO y creación de contenido útil."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ]
                    },
                    timeout=120
                )

                print(f"[DEBUG] Status ({model}):", response.status_code)

                # Rate limit → reintentar
                if response.status_code == 429:
                    wait_time = 10 * (attempt + 1)
                    print(f"[RETRY] Rate limit en {model}. Esperando {wait_time}s...")
                    time.sleep(wait_time)
                    continue

                # Modelo no disponible → siguiente modelo
                if response.status_code == 404:
                    print(f"[SKIP] Modelo no disponible: {model}")
                    break

                data = response.json()

                if "choices" in data and len(data["choices"]) > 0:
                    choice = data["choices"][0]

                    if "message" in choice and "content" in choice["message"]:
                        print(f"[OK] Modelo usado: {model}")
                        return choice["message"]["content"]

                    if "text" in choice:
                        print(f"[OK] Modelo usado: {model}")
                        return choice["text"]

                print("[ERROR] Respuesta inesperada:", data)
                break

            except Exception as e:
                print(f"[ERROR] Excepción con {model}: {e}")
                break

    print("[FAIL] Ningún modelo ha funcionado")
    return None


# =========================
# 🧠 GENERAR TOPIC
# =========================
def generate_topic():
    prompt = """
Genera 5 ideas de artículos SEO en español con estas condiciones:

- nicho rentable (dinero, tecnología, software, salud)
- intención de búsqueda clara
- long-tail (mínimo 5 palabras)
- orientado a resolver un problema concreto

Devuelve solo la lista.
"""

    response = call_llm(prompt)

    if not response:
        print("[FALLBACK] Usando topic predefinido")
        return random.choice(FALLBACK_TOPICS)

    topics = [
        t.strip("- ").strip()
        for t in response.split("\n")
        if t.strip()
    ]

    print("[DEBUG] Topics generados:", topics)

    return random.choice(topics) if topics else random.choice(FALLBACK_TOPICS)


# =========================
# ✅ VALIDACIÓN
# =========================
def is_valid_article(content):
    if not content:
        return False

    if len(content) < 800:
        return False

    if "lorem" in content.lower():
        return False

    return True


# =========================
# ✍️ GENERAR ARTÍCULO
# =========================
def generate_article(topic):
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{CONTENT_DIR}/article_{now}.md"

    prompt = f"""
Escribe un artículo SEO en español sobre "{topic}".

IMPORTANTE:
- Responde a una duda concreta
- Incluye ejemplos reales
- Incluye comparativas si aplica
- Evita frases genéricas
- Aporta valor real

Estructura:
- H1 claro
- H2 útiles
- listas prácticas
- conclusión accionable

El objetivo es que el usuario no tenga que buscar en otro sitio.
"""

    content = call_llm(prompt)

    if not is_valid_article(content):
        print("[SKIP] Contenido no válido")
        return

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[OK] Artículo generado: {filename}")


# =========================
# 🔁 JOB
# =========================
def job():
    topic = generate_topic()
    print(f"[INFO] Topic elegido: {topic}")
    generate_article(topic)


print("[START] Agent worker iniciado...")

# Ejecutar uno al inicio
job()

# Frecuencia controlada
schedule.every().day.at("10:00").do(job)
schedule.every().day.at("18:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(30)
