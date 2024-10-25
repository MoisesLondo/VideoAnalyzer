import os
import tempfile
from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse
import moviepy.editor as mp
import whisper
from langchain_ollama import OllamaLLM
from textblob import TextBlob
from langdetect import detect

nltk.download('punkt')
nltk.download('stopwords')

@api_view(['POST'])
def videoText(request):
    try:
        video_file = request.FILES.get('file')
        if not video_file:
            return JsonResponse({'error': 'No se proporcionó ningún archivo'}, status=status.HTTP_400_BAD_REQUEST)

        # Validar tipo de archivo
        if not video_file.name.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            return JsonResponse({'error': 'Tipo de archivo inválido'}, status=status.HTTP_400_BAD_REQUEST)

        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            temp_file_path = temp_file.name
            for chunk in video_file.chunks():
                temp_file.write(chunk)

        with mp.VideoFileClip(temp_file_path) as video:
            # Extraer metadatos del video
            duracion = video.duration
            fps = video.fps
            tamano = video.size

            audio_path = f'{temp_file_path}.wav'
            video.audio.write_audiofile(audio_path)


        transcripcion = whisper_test(audio_path)
        ideas_titulo = chat(f'Dame 3 ideas de títulos para la siguiente descripción: {transcripcion}. No me des introducción, solo las ideas')
        resumen = chat(f'Hazme un resumen para la siguiente transcripción: {transcripcion}. No me des introducción, solo el resumen')

        # Análisis de sentimiento
        sentimiento = TextBlob(transcripcion).sentiment.polarity

        # Detección de idioma
        idioma = detect(transcripcion)

        # Generar capítulos del video
        capitulos = chat(f'Genera 5 títulos de capítulos con marcas de tiempo para un video basado en esta transcripción: {transcripcion}. Formatea como "MM:SS - Título del Capítulo".')

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
            'idioma': idioma,
            'capitulos': capitulos
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def whisper_test(audio_path):
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    print(result['text'])
    return result['text']

def chat(myprompt):
    model = OllamaLLM(model="llama3.2")
    result = model.invoke(input=f"{myprompt}")
    print(result)
    return result