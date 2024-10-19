from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import tempfile
from scrap import fetch_iframe_src  # Importar diretamente do scrap.py
from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip
import requests
import uuid

app = FastAPI()

# Diretório onde os vídeos serão salvos
video_directory = "videos"

ORIENTATION_DIMENSIONS = {
    "horizontal": "horizontal.jpg",  # 16:9
    "vertical": "vertical.jpg",    # 9:16
}

# Certifique-se de que o diretório "videos" exista
if not os.path.exists(video_directory):
    os.makedirs(video_directory)

# Modelo de dados para requisições POST
class URLModel(BaseModel):
    url: str

app.mount("/videos", StaticFiles(directory="videos"), name="videos")

@app.post("/scrap")
async def scrap_iframe_src_api(url_model: URLModel):
    url = url_model.url
    try:
        iframe_src = fetch_iframe_src(url)
        if iframe_src:
            return {"iframeSrc": iframe_src}
        else:
            raise HTTPException(status_code=404, detail="No iframe src found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch iframe src: {str(e)}")

@app.post("/time")
async def get_video_duration(url_model: URLModel):
    url = url_model.url
    try:
        # Fazer o download do vídeo
        response = requests.get(url, stream=True)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to download the video")

        # Criar um arquivo temporário para salvar o vídeo
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    temp_video_file.write(chunk)

            temp_video_path = temp_video_file.name  # Obter o caminho do arquivo temporário

        # Usar o MoviePy para obter a duração do vídeo
        try:
            with VideoFileClip(temp_video_path) as video_clip:
                duration_in_seconds = video_clip.duration
        finally:
            # Remover o arquivo temporário após o uso
            os.remove(temp_video_path)

        return {"duration": duration_in_seconds}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process video: {str(e)}")

@app.post("/convert")
async def upload_and_convert(
    file: UploadFile = File(...),
    orientation: str = Query("horizontal", enum=["horizontal", "vertical"])
):
    try:
        # Verifica se o arquivo é um .mp3
        if not file.filename.endswith(".mp3"):
            raise HTTPException(status_code=400, detail="Only .mp3 files are supported")

        file_uuid = str(uuid.uuid4())

        # Salva o arquivo .mp3 temporariamente na pasta 'videos'
        mp3_file_path = os.path.join(video_directory, f"{file_uuid}.mp3")
        with open(mp3_file_path, "wb") as f:
            f.write(await file.read())

        # Defina o caminho de saída para o arquivo convertido .mp4
        mp4_file_path = os.path.join(video_directory, f"{file_uuid}.mp4")

        # Converte o arquivo .mp3 para .mp4 usando MoviePy
        try:
            # Carrega o áudio
            audio_clip = AudioFileClip(mp3_file_path)

            # Define as dimensões com base na plataforma
            image_path = ORIENTATION_DIMENSIONS[orientation]

            # Carrega uma imagem de fundo ou cria uma imagem colorida (exemplo: 1280x720 pixels, cor preta)
            image_clip = ImageClip(image_path, duration=audio_clip.duration).set_duration(audio_clip.duration).set_fps(24)

            # Define o áudio no clip da imagem
            video_clip = image_clip.set_audio(audio_clip)

            # Salva o arquivo .mp4
            video_clip.write_videofile(mp4_file_path, codec="libx264", fps=24)

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to convert file: {str(e)}")

        os.remove(mp3_file_path)

        # Retorna o caminho do arquivo .mp4 convertido e URL pública
        return {
            "message": "File uploaded and converted successfully",
            "mp4_file": f"http://134.209.217.198/videos/{os.path.basename(mp4_file_path)}",
            "delete_request": f"http://134.209.217.198/delete/{os.path.basename(mp4_file_path)}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload and convert video: {str(e)}")

@app.delete("/delete/{filename}")
async def delete_video(filename: str):
    try:
        # Caminho completo para o arquivo na pasta 'videos'
        file_path = os.path.join(video_directory, filename)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            return {"message": f"File {filename} has been deleted"}
        else:
            raise HTTPException(status_code=404, detail="File not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete video: {str(e)}")

@app.get("/")
async def read_root():
    return {"message": "API ok"}
