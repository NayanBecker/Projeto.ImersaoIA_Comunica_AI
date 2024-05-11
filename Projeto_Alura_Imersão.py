import streamlit as st
from pathlib import Path
import hashlib
import google.generativeai as genai
import cv2
import os
import shutil
import tempfile
genai.configure(api_key="AIzaSyC_yCVTTBzLoj76dJGqRkkKBHmOrjVybTc")

# Set up the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 0,
  "max_output_tokens": 8192,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]

system_instruction = "Fale tudo como se fosse um especialista em Oratória, que avalia e ajuda a melhorar a comunicação e oratoria de outras pessoas, responda sempre com dicas simples e peça sempre um retorno de seu cliente"

model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                              generation_config=generation_config,
                              system_instruction=system_instruction,
                              safety_settings=safety_settings)

import cv2

class File:
  def __init__(self, file_path: str, display_name: str = None):
    self.file_path = file_path
    if display_name:
      self.display_name = display_name
    self.timestamp = get_timestamp(file_path)

  def set_file_response(self, response):
    self.response = response
def get_timestamp(filename):
  """Extracts the frame count (as an integer) from a filename with the format
     'output_file_prefix_frame00:00.jpg'.
  """
  parts = filename.split(FRAME_PREFIX)
  if len(parts) != 2:
      return None  # Indicates the filename might be incorrectly formatted
  return parts[1].split('.')[0]

# Create or cleanup existing extracted image frames directory.
FRAME_EXTRACTION_DIRECTORY = "content/frames"
FRAME_PREFIX = "_frame"
def create_frame_output_dir(output_dir):
  if not os.path.exists(output_dir):
    os.makedirs(output_dir)
  else:
    shutil.rmtree(output_dir)
    os.makedirs(output_dir)

def extract_frame_from_video(video_file_path):
  print(f"Extracting {video_file_path} at 1 frame per second. This might take a bit...")
  create_frame_output_dir(FRAME_EXTRACTION_DIRECTORY)
  vidcap = cv2.VideoCapture(video_file_path)
  fps = vidcap.get(cv2.CAP_PROP_FPS)
  frame_duration = 1 / fps  # Time interval between frames (in seconds)
  output_file_prefix = os.path.basename(video_file_path).replace('.', '_')
  frame_count = 0
  count = 0
  while vidcap.isOpened():
      success, frame = vidcap.read()
      if not success: # End of video
          break
      if int(count / fps) == frame_count: # Extract a frame every second
          min = frame_count // 60
          sec = frame_count % 60
          time_string = f"{min:02d}:{sec:02d}"
          image_name = f"{output_file_prefix}{FRAME_PREFIX}{time_string}.jpg"
          output_filename = os.path.join(FRAME_EXTRACTION_DIRECTORY, image_name)
          cv2.imwrite(output_filename, frame)
          frame_count += 1
      count += 1
  vidcap.release() # Release the capture object\n",
  print(f"Completed video frame extraction!\n\nExtracted: {frame_count} frames")


convo = model.start_chat(history=[])

# Título do aplicativo Streamlit
st.title("Comunica_AI")

# Widget para upload de vídeo
uploaded_video = st.file_uploader("Envie o seu Video para Avaliação! ", type=["mp4"])
def make_request(prompt, files):
  request = [prompt]
  for file in files:
    request.append(file.timestamp)
    request.append(file.response)
  return request
  
  
if uploaded_video is not None:
  # Exibe o vídeo carregado
  st.video(uploaded_video)
  #video_bytes = uploaded_video.read()
  temp_file_path=""
  with tempfile.NamedTemporaryFile(delete=False) as temp_file:
	  temp_file.write(uploaded_video.read())
	  temp_file_path = temp_file.name
  # Extrair frames do vídeo
  print (temp_file_path)
  print (uploaded_video)
  print (uploaded_video.name)
  frames = extract_frame_from_video(temp_file_path) 
  
  files = os.listdir(FRAME_EXTRACTION_DIRECTORY)
  files = sorted(files)

  files_to_upload = []
  for file in files:
    files_to_upload.append(File(file_path=os.path.join(FRAME_EXTRACTION_DIRECTORY, file)))
  full_video = False
  uploaded_files = []
  print(f'Uploading {len(files_to_upload) if full_video else 10} files. This might take a bit...')

  for file in files_to_upload:
    print(f'Uploading: {file.file_path}...')
    response = genai.upload_file(path=file.file_path)
    file.set_file_response(response)
    uploaded_files.append(file)
  
  request = make_request("identifique neste vídeo momentos em que pode ser melhorada a orataria, quero que você de Dicas de melhorias, e o por que de estar Corrigindo o modo de oratoria da pessoa. Preciso que seja identificado: Comunicação verbal como, repetições de palavras, tons da voz; Comunicação não verbal como, postura da pessoa, maneira que utiliza as mãos para explicar, e expressões facias. Escreva em Português, Brasil. ", files_to_upload)
  response = model.generate_content(request,
                                  request_options={"timeout": 600})
  st.write(response.text)

  
  
