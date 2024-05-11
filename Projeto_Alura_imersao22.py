import streamlit as st
import google.generativeai as genai
import cv2
import os
import shutil
import tempfile

# Configurar a chave da API
genai.configure(api_key="AIzaSyC_yCVTTBzLoj76dJGqRkkKBHmOrjVybTc")

# Definir configurações de geração
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 0,
    "max_output_tokens": 8192,
}

# Definir configurações de segurança
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# Iniciar modelo
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    generation_config=generation_config,
    system_instruction="Fale tudo como se fosse um especialista em Oratória, que avalia e ajuda a melhorar a comunicação e oratoria de outras pessoas, responda sempre com dicas simples e peça sempre um retorno de seu cliente",
    safety_settings=safety_settings,
)

# Título do aplicativo Streamlit
st.title("Comunica_AI")

# Widget para upload de vídeo
uploaded_video = st.file_uploader("Envie o seu Vídeo para Avaliação!", type=["mp4"])

if uploaded_video is not None:
    # Exibir o vídeo carregado
    st.video(uploaded_video)

    # Extrair frames do vídeo
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(uploaded_video.read())
        temp_file_path = temp_file.name

    # Fazer upload dos frames
    frames = extract_frame_from_video(temp_file_path)
    uploaded_files = upload_frames(frames)

    # Gerar conteúdo
    request = make_request("identifique neste vídeo momentos em que pode ser melhorada a orataria, quero que você de Dicas de melhorias, e o por que de estar Corrigindo o modo de oratoria da pessoa. Preciso que seja identificado: Comunicação verbal como, repetições de palavras, tons da voz; Comunicação não verbal como, postura da pessoa, maneira que utiliza as mãos para explicar, e expressões facias. Escreva em Português, Brasil. ", uploaded_files)
    response = model.generate_content(request, request_options={"timeout": 600})
    st.write(response.text)
