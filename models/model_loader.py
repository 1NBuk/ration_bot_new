from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    AutoImageProcessor,
    ViTForImageClassification,
    AutoModelForSeq2SeqLM
)

def load_models():
    model_id = "vikhyatk/moondream2"
    revision = "2024-08-26"

    model2 = AutoModelForCausalLM.from_pretrained(
        model_id, trust_remote_code=True, revision=revision
    )
    tokenizer2 = AutoTokenizer.from_pretrained(model_id, revision=revision)

    image_processor = AutoImageProcessor.from_pretrained("nateraw/food")
    model1 = ViTForImageClassification.from_pretrained("nateraw/food")

    tokenizer3 = AutoTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-ru")
    model3 = AutoModelForSeq2SeqLM.from_pretrained("Helsinki-NLP/opus-mt-en-ru")

    return model1, image_processor, model2, tokenizer2, model3, tokenizer3
