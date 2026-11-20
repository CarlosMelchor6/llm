import os

import streamlit as st
from google import genai
from google.genai import errors, types


NOMBRE_DEL_MODELO = "gemini-3.8-flash"
TIEMPO_ESPERA_MS = 180_000
MAX_TOKENS_SALIDA = 2_048


def mejorar_texto(api_key: str, texto_original: str) -> str:
    client = genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(timeout=TIEMPO_ESPERA_MS),
    )
    prompt = """Actúa como un corrector profesional de textos en español.
Corrige ortografía, gramática, puntuación y mejora la claridad y fluidez sin
cambiar el significado ni inventar información. Conserva el formato de
párrafos. Devuelve únicamente el texto corregido, sin comentarios ni comillas.

Texto original:
{text}
"""
    response = client.models.generate_content(
        model=NOMBRE_DEL_MODELO,
        contents=prompt.format(text=texto_original),
        config=types.GenerateContentConfig(
            max_output_tokens=MAX_TOKENS_SALIDA,
        ),
    )
    texto_mejorado = (response.text or "").strip()
    if not texto_mejorado:
        raise RuntimeError("La API no devolvió un texto corregido.")
    return texto_mejorado


def main() -> None:
    st.set_page_config(
        page_title="Mejorar redacción y ortografía",
        layout="centered",
    )

    st.title("Mejorar redacción y ortografía")
    st.write(
        "Pega un texto y Gemini corregirá sus errores y mejorará su claridad "
        "sin cambiar el significado."
    )

    api_por_defecto = os.getenv("GOOGLE_API_KEY", "")
    api_key = st.text_input(
        "API key de Google Gemini",
        value=api_por_defecto,
        type="password",
        placeholder="Ingresa tu API key de Google Gemini...",        
    )

    texto_original = st.text_area(
        "Texto a mejorar",
        height=250,
        placeholder="Escribe o pega aquí el texto que quieres mejorar...",
    )

    if st.button("Mejorar texto", type="primary"):
        if not api_key.strip():
            st.error("Ingresa una API key de Google Gemini para continuar.")
            return
        if not texto_original.strip():
            st.warning("Ingresa un texto para mejorar.")
            return

        with st.spinner("Revisando el texto..."):
            try:
                texto_mejorado = mejorar_texto(api_key.strip(), texto_original.strip())
            except (errors.APIError, RuntimeError, ValueError) as error:
                st.error(f"No fue posible mejorar el texto: {error}")
                return

        st.subheader("Texto mejorado")
        st.text_area("Resultado", value=texto_mejorado, height=250)
        st.download_button(
            "Descargar resultado",
            data=texto_mejorado,
            file_name="texto_mejorado.txt",
            mime="text/plain",
        )


if __name__ == "__main__":
    main()


# streamlit run app.pyC