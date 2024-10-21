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
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
        video = mp.VideoFileClip(video_file.temporary_file_path())
        video.audio.write_audiofile(temp_audio.name)
        video.close()
        transcription = whisper_test(temp_audio.name)
        result = chat(f'Dame 3 ideas de titulos para la siguiente descripción: {transcription}. No me des introducción, solo las ideas')
        resumen = chat(f'Hazme un resumen para la siguiente descripción: {transcription}. No me des introducción, solo el resumen')
    os.unlink(temp_audio.name)
    
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