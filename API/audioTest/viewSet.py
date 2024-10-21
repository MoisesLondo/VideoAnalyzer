import os
import tempfile
from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse
import moviepy.editor as mp
import whisper
from langchain_ollama import OllamaLLM


@api_view(['POST'])
def videoText(request):
    video_file = request.FILES['video']

    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
        temp_file_path = temp_file.name

        with open(temp_file_path, 'wb') as f:
            for chunk in video_file.chunks():
                f.write(chunk)

    with mp.VideoFileClip(temp_file_path) as video:
        audio_path = f'{temp_file_path}.wav'
        video.audio.write_audiofile(audio_path)

    transcription = whisper_test(audio_path)
    result = chat(f'Dame 3 ideas de titulos para la siguiente descripción: {transcription}. No me des introducción, solo las ideas')
    resumen = chat(f'Hazme un resumen para la siguiente descripción: {transcription}. No me des introducción, solo el resumen')

    os.unlink(temp_file_path)
    os.unlink(audio_path)

    return JsonResponse({'text': transcription, 'ideas': result, 'resumen': resumen}, status=status.HTTP_200_OK)

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