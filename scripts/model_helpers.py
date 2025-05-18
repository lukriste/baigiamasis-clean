from transformers import TFAutoModelForSeq2SeqLM, T5Tokenizer
import tensorflow as tf

# Įkeliame išsaugotą modelį
model = TFAutoModelForSeq2SeqLM.from_pretrained("gnm-t5")
tokenizer = T5Tokenizer.from_pretrained("gnm-t5")

def gauti_modelio_atsakyma(simptomas: str, ivestis: str) -> str:
    if not simptomas:
        return "Reikia nurodyti bent simptomą."

    tekstas = f"simptomas: {simptomas}."
    if ivestis:
        tekstas += f" situacija: {ivestis}"

    try:
        input_ids = tokenizer(tekstas, return_tensors="tf", truncation=True, padding=True).input_ids
        output_ids = model.generate(input_ids, max_length=128)
        atsakymas = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        return atsakymas
    except Exception as e:
        return f"Klaida generuojant atsakymą: {str(e)}"