import { HfInference } from '@huggingface/inference'

const hf = new HfInference('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')
const url = 'https://m.media-amazon.com/images/M/MV5BYWVjODZjNDgtYjk4ZS00OTg5LTg5NDQtZDMxZDQ4ZmM5MGJmXkEyXkFqcGc@._V1_.jpg'

const res = await fetch(url)
const image = await res.blob()

const imageDescription = await hf.imageToText({
    data: image,
    model: 'Salesforce/blip-image-captioning-large'
})

const newPhrase = await hf.translation({
    model: 'Helsinki-NLP/opus-mt-en-es',
    inputs: imageDescription.generated_text,
    parameters: {
    "src_lang": "en",
    "tgt_lang": "es"
   }
  })

console.log(imageDescription)
console.log(newPhrase)
