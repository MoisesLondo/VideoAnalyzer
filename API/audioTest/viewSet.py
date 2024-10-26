import os
import tempfile
from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse
import moviepy.editor as mp
import whisper
from textblob import TextBlob
from langdetect import detect
from groq import Groq
import yt_dlp

@api_view(['POST'])
def videoText(request):
    try:
        video_file = request.FILES.get('file')
        if not video_file:
            return JsonResponse({'error': 'No se proporcionó ningún archivo'}, status=status.HTTP_400_BAD_REQUEST)

        if not video_file.name.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            return JsonResponse({'error': 'Tipo de archivo inválido'}, status=status.HTTP_400_BAD_REQUEST)

        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            temp_file_path = temp_file.name
            for chunk in video_file.chunks():
                temp_file.write(chunk)

        with mp.VideoFileClip(temp_file_path) as video:
            duracion = video.duration
            fps = video.fps
            tamano = video.size

            audio_path = f'{temp_file_path}.wav'
            video.audio.write_audiofile(audio_path)


        transcripcion = whisper_test(audio_path)
        ideas_titulo = chat(f'Dame 3 ideas de títulos para la siguiente descripción: {transcripcion}. No me des introducción, solo las ideas')
        resumen = chat(f'Hazme un resumen para la siguiente transcripción: {transcripcion}. No me des introducción, solo el resumen')

        sentimiento = TextBlob(transcripcion).sentiment.polarity

        idioma = detect(transcripcion)


        os.unlink(temp_file_path)
        os.unlink(audio_path)

        return JsonResponse({
            'text': transcripcion,
            'ideas': ideas_titulo,
            'resumen': resumen,
            'metadatos': {
                'duracion': duracion,
                'fps': fps,
                'tamano': tamano
            },
            'sentimiento': sentimiento,
            'idioma': idioma
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def linkText(request):
    try:
        link = request.data.get('link')
        if not link:
            return JsonResponse({'error': 'No se proporcionó ningún enlace'}, status=status.HTTP_400_BAD_REQUEST)
        
        path = 'C:/Users/ACUS/Desktop/Video-Test'
        temp_dir = tempfile.TemporaryDirectory()
        print(temp_dir.name)
            
        title, author, length, thumbnail, category=downloadLink(link, temp_dir.name)
        audio_path = temp_dir.name + 'audio.mp3'
        print(audio_path)
        
        transcripcion = whisper_test(audio_path)
        ideas_titulo = chat(f'Dame 3 ideas de títulos para la siguiente descripción: {transcripcion}. No me des introducción, solo las ideas')
        resumen = chat(f'Hazme un resumen para la siguiente transcripción: {transcripcion}. No me des introducción, solo el resumen')
        idioma = detect(transcripcion)
        return JsonResponse({
            'title': title,
            'length': f'{length//60}:{length%60:02d}',
            'author': author,
            'text': transcripcion,
            'ideas': ideas_titulo,
            'resumen': resumen,
            'idioma': idioma,
            'thumbnail': thumbnail,
            'category': category,
        }, status=status.HTTP_200_OK)

    except Exception as e:
        print(e)
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def whisper_test(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    print(result['text'])
    return result['text']

def chat(myprompt):
    key = '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'
    client = Groq(api_key=key)
    completion = client.chat.completions.create(
    model="llama3-8b-8192",
    messages= [{
            "role": "user",
            "content": myprompt,
        }],
    )
    return completion.choices[0].message.content

def downloadLink(url, output_path):
    ydl_opts = {
        'extract_audio': True,
        'outtmpl': output_path + 'audio.mp3',
        'format': 'bestaudio'
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        
        title = info.get('title', 'No title available')
        author = info.get('uploader', 'No author available')
        length = info.get('duration', 0)
        thumbnail = info.get('thumbnail', '')
        category = info.get('channel', 'Unknown Category')
        
        print(f"Title: {title}")
        print(f"Author: {author}")
        print(f"Duration: {length} seconds")
        print(f"Thumbnail: {thumbnail}")
        print(f"Category: {category}")
        
        return title, author, length, thumbnail, category