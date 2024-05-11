{
  "nbformat": 4,
  "nbformat_minor": 0,
  "metadata": {
    "colab": {
      "provenance": [],
      "authorship_tag": "ABX9TyNi3OIwrLmBHczTDKiiZx/t",
      "include_colab_link": true
    },
    "kernelspec": {
      "name": "python3",
      "display_name": "Python 3"
    },
    "language_info": {
      "name": "python"
    }
  },
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {
        "id": "view-in-github",
        "colab_type": "text"
      },
      "source": [
        "<a href=\"https://colab.research.google.com/github/NayanBecker/Projeto.ImersaoIA_Comunica_AI/blob/main/Projeto_Alura_Imers%C3%A3o.py\" target=\"_parent\"><img src=\"https://colab.research.google.com/assets/colab-badge.svg\" alt=\"Open In Colab\"/></a>"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": 3,
      "metadata": {
        "id": "Wx95giKziOkV"
      },
      "outputs": [],
      "source": [
        "!pip install -q -U google-generativeai"
      ]
    },
    {
      "cell_type": "code",
      "source": [
        "import google.generativeai as genai\n",
        "from google.colab import userdata\n",
        "api_key = userdata.get('SECRET_KEY')\n",
        "genai.configure(api_key=api_key)"
      ],
      "metadata": {
        "id": "_Pe51rcBpD3y"
      },
      "execution_count": 9,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "!pip install streamlit"
      ],
      "metadata": {
        "id": "lv2zVavSo3Yz"
      },
      "execution_count": null,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "import streamlit as st\n",
        "from pathlib import Path\n",
        "import hashlib\n",
        "import google.generativeai as genai\n",
        "import cv2\n",
        "import os\n",
        "import shutil\n",
        "import tempfile\n",
        "genai.configure(api_key=\"AIzaSyC_yCVTTBzLoj76dJGqRkkKBHmOrjVybTc\")\n",
        "\n",
        "# Set up the model\n",
        "generation_config = {\n",
        "  \"temperature\": 1,\n",
        "  \"top_p\": 0.95,\n",
        "  \"top_k\": 0,\n",
        "  \"max_output_tokens\": 8192,\n",
        "}\n",
        "\n",
        "safety_settings = [\n",
        "  {\n",
        "    \"category\": \"HARM_CATEGORY_HARASSMENT\",\n",
        "    \"threshold\": \"BLOCK_MEDIUM_AND_ABOVE\"\n",
        "  },\n",
        "  {\n",
        "    \"category\": \"HARM_CATEGORY_HATE_SPEECH\",\n",
        "    \"threshold\": \"BLOCK_MEDIUM_AND_ABOVE\"\n",
        "  },\n",
        "  {\n",
        "    \"category\": \"HARM_CATEGORY_SEXUALLY_EXPLICIT\",\n",
        "    \"threshold\": \"BLOCK_MEDIUM_AND_ABOVE\"\n",
        "  },\n",
        "  {\n",
        "    \"category\": \"HARM_CATEGORY_DANGEROUS_CONTENT\",\n",
        "    \"threshold\": \"BLOCK_MEDIUM_AND_ABOVE\"\n",
        "  },\n",
        "]\n",
        "\n",
        "system_instruction = \"Fale tudo como se fosse um especialista em Oratória, que avalia e ajuda a melhorar a comunicação e oratoria de outras pessoas, responda sempre com dicas simples e peça sempre um retorno de seu cliente\"\n",
        "\n",
        "model = genai.GenerativeModel(model_name=\"gemini-1.5-pro-latest\",\n",
        "                              generation_config=generation_config,\n",
        "                              system_instruction=system_instruction,\n",
        "                              safety_settings=safety_settings)\n",
        "\n",
        "import cv2\n",
        "\n",
        "class File:\n",
        "  def __init__(self, file_path: str, display_name: str = None):\n",
        "    self.file_path = file_path\n",
        "    if display_name:\n",
        "      self.display_name = display_name\n",
        "    self.timestamp = get_timestamp(file_path)\n",
        "\n",
        "  def set_file_response(self, response):\n",
        "    self.response = response\n",
        "def get_timestamp(filename):\n",
        "  \"\"\"Extracts the frame count (as an integer) from a filename with the format\n",
        "     'output_file_prefix_frame00:00.jpg'.\n",
        "  \"\"\"\n",
        "  parts = filename.split(FRAME_PREFIX)\n",
        "  if len(parts) != 2:\n",
        "      return None  # Indicates the filename might be incorrectly formatted\n",
        "  return parts[1].split('.')[0]\n",
        "\n",
        "# Create or cleanup existing extracted image frames directory.\n",
        "FRAME_EXTRACTION_DIRECTORY = \"content/frames\"\n",
        "FRAME_PREFIX = \"_frame\"\n",
        "def create_frame_output_dir(output_dir):\n",
        "  if not os.path.exists(output_dir):\n",
        "    os.makedirs(output_dir)\n",
        "  else:\n",
        "    shutil.rmtree(output_dir)\n",
        "    os.makedirs(output_dir)\n",
        "\n",
        "def extract_frame_from_video(video_file_path):\n",
        "  print(f\"Extracting {video_file_path} at 1 frame per second. This might take a bit...\")\n",
        "  create_frame_output_dir(FRAME_EXTRACTION_DIRECTORY)\n",
        "  vidcap = cv2.VideoCapture(video_file_path)\n",
        "  fps = vidcap.get(cv2.CAP_PROP_FPS)\n",
        "  frame_duration = 1 / fps  # Time interval between frames (in seconds)\n",
        "  output_file_prefix = os.path.basename(video_file_path).replace('.', '_')\n",
        "  frame_count = 0\n",
        "  count = 0\n",
        "  while vidcap.isOpened():\n",
        "      success, frame = vidcap.read()\n",
        "      if not success: # End of video\n",
        "          break\n",
        "      if int(count / fps) == frame_count: # Extract a frame every second\n",
        "          min = frame_count // 60\n",
        "          sec = frame_count % 60\n",
        "          time_string = f\"{min:02d}:{sec:02d}\"\n",
        "          image_name = f\"{output_file_prefix}{FRAME_PREFIX}{time_string}.jpg\"\n",
        "          output_filename = os.path.join(FRAME_EXTRACTION_DIRECTORY, image_name)\n",
        "          cv2.imwrite(output_filename, frame)\n",
        "          frame_count += 1\n",
        "      count += 1\n",
        "  vidcap.release() # Release the capture object\\n\",\n",
        "  print(f\"Completed video frame extraction!\\n\\nExtracted: {frame_count} frames\")\n",
        "\n",
        "\n",
        "convo = model.start_chat(history=[])\n",
        "\n",
        "# Título do aplicativo Streamlit\n",
        "st.title(\"Comunica_AI\")\n",
        "\n",
        "# Widget para upload de vídeo\n",
        "uploaded_video = st.file_uploader(\"Envie o seu Video para Avaliação! \", type=[\"mp4\"])\n",
        "def make_request(prompt, files):\n",
        "  request = [prompt]\n",
        "  for file in files:\n",
        "    request.append(file.timestamp)\n",
        "    request.append(file.response)\n",
        "  return request\n",
        "\n",
        "\n",
        "if uploaded_video is not None:\n",
        "  # Exibe o vídeo carregado\n",
        "  st.video(uploaded_video)\n",
        "  #video_bytes = uploaded_video.read()\n",
        "  temp_file_path=\"\"\n",
        "  with tempfile.NamedTemporaryFile(delete=False) as temp_file:\n",
        "\t  temp_file.write(uploaded_video.read())\n",
        "\t  temp_file_path = temp_file.name\n",
        "  # Extrair frames do vídeo\n",
        "  print (temp_file_path)\n",
        "  print (uploaded_video)\n",
        "  print (uploaded_video.name)\n",
        "  frames = extract_frame_from_video(temp_file_path)\n",
        "\n",
        "  files = os.listdir(FRAME_EXTRACTION_DIRECTORY)\n",
        "  files = sorted(files)\n",
        "\n",
        "  files_to_upload = []\n",
        "  for file in files:\n",
        "    files_to_upload.append(File(file_path=os.path.join(FRAME_EXTRACTION_DIRECTORY, file)))\n",
        "  full_video = False\n",
        "  uploaded_files = []\n",
        "  print(f'Uploading {len(files_to_upload) if full_video else 10} files. This might take a bit...')\n",
        "\n",
        "  for file in files_to_upload:\n",
        "    print(f'Uploading: {file.file_path}...')\n",
        "    response = genai.upload_file(path=file.file_path)\n",
        "    file.set_file_response(response)\n",
        "    uploaded_files.append(file)\n",
        "\n",
        "  request = make_request(\"identifique neste vídeo momentos em que pode ser melhorada a orataria, quero que você de Dicas de melhorias, e o por que de estar Corrigindo o modo de oratoria da pessoa. Preciso que seja identificado: Comunicação verbal como, repetições de palavras, tons da voz; Comunicação não verbal como, postura da pessoa, maneira que utiliza as mãos para explicar, e expressões facias. Escreva em Português, Brasil. \", files_to_upload)\n",
        "  response = model.generate_content(request,\n",
        "                                  request_options={\"timeout\": 600})\n",
        "  st.write(response.text)\n",
        "\n",
        "\n",
        ""
      ],
      "metadata": {
        "id": "EP1AY_wli5-W"
      },
      "execution_count": 11,
      "outputs": []
    },
    {
      "cell_type": "code",
      "source": [
        "!streamlit run /usr/local/lib/python3.10/dist-packages/colab_kernel_launcher.py"
      ],
      "metadata": {
        "colab": {
          "base_uri": "https://localhost:8080/"
        },
        "id": "wIk2YUOep4BB",
        "outputId": "2fcfca80-c822-4733-b36e-4f19417b2afa"
      },
      "execution_count": 12,
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": [
            "\n",
            "Collecting usage statistics. To deactivate, set browser.gatherUsageStats to false.\n",
            "\u001b[0m\n",
            "\u001b[0m\n",
            "\u001b[34m\u001b[1m  You can now view your Streamlit app in your browser.\u001b[0m\n",
            "\u001b[0m\n",
            "\u001b[34m  Network URL: \u001b[0m\u001b[1mhttp://172.28.0.12:8501\u001b[0m\n",
            "\u001b[34m  External URL: \u001b[0m\u001b[1mhttp://34.83.253.89:8501\u001b[0m\n",
            "\u001b[0m\n",
            "\u001b[34m  Stopping...\u001b[0m\n",
            "\u001b[34m  Stopping...\u001b[0m\n"
          ]
        }
      ]
    }
  ]
}