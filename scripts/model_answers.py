from transformers import TFAutoModelForSeq2SeqLM, T5Tokenizer
import tensorflow as tf

# Įkeliame išsaugotą modelį
model = TFAutoModelForSeq2SeqLM.from_pretrained("gnm-t5")
tokenizer = T5Tokenizer.from_pretrained("gnm-t5")

def gauti_modelio_atsakyma(simptomas: str, ivestis: str) -> str:
    tekstas = f"simptomas: {simptomas}. {ivestis}"
    input_ids = tokenizer(tekstas, return_tensors="tf", truncation=True, padding=True).input_ids
    output_ids = model.generate(input_ids, max_length=128)
    atsakymas = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return atsakymas