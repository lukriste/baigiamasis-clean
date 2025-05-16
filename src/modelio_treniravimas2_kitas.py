import os
os.environ["TF_USE_LEGACY_KERAS"] = "1"

import pandas as pd
import re
from sqlalchemy import create_engine
from transformers import T5Tokenizer, T5Config, TFAutoModelForSeq2SeqLM, DataCollatorForSeq2Seq
from datasets import Dataset
from sklearn.model_selection import train_test_split
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.keras.optimizers.legacy import Adam
from tensorflow.keras.losses import SparseCategoricalCrossentropy





engine = create_engine("mysql+pymysql://lukriste:Astikiusavimi100@localhost/gnm1")
df = pd.read_sql("SELECT simptomas, ivestis, isvestis FROM simptomai", con=engine)


df["input"] = "simptomas: " + df["simptomas"] + ". " + df["ivestis"]
df["target"] = df["isvestis"]

data = df[["input", "target"]]

train_df, test_df = train_test_split(data, test_size=0.1, random_state=42)

train_dataset = Dataset.from_pandas(train_df.reset_index(drop=True))
test_dataset = Dataset.from_pandas(test_df.reset_index(drop=True))

tokenizer = T5Tokenizer.from_pretrained("LukasStankevicius/t5-base-lithuanian-news-summaries-175")

def tokenize_function(example):
    input_enc = tokenizer(example["input"], padding="max_length", truncation=True, max_length=128)
    output_enc = tokenizer(example["target"], padding="max_length", truncation=True, max_length=128)
    input_enc["labels"] = output_enc["input_ids"]
    return input_enc

train_tokenized = train_dataset.map(tokenize_function, batched=False, remove_columns=["input", "target"])
test_tokenized = test_dataset.map(tokenize_function, batched=False, remove_columns=["input", "target"])

model = TFAutoModelForSeq2SeqLM.from_pretrained("LukasStankevicius/t5-base-lithuanian-news-summaries-175", from_pt=True)

data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model, return_tensors="tf")

train_set = train_tokenized.to_tf_dataset(
    shuffle=True,
    batch_size=4,
    collate_fn=data_collator
)

val_set = test_tokenized.to_tf_dataset(
    shuffle=False,
    batch_size=4,
    collate_fn=data_collator
)

model.compile(
    optimizer=Adam(learning_rate=5e-5),
    loss=SparseCategoricalCrossentropy(from_logits=True)
)

history = model.fit(
    train_set,
    validation_data=val_set,
    epochs=20
    )

model.save_pretrained("gnm-t5")
tokenizer.save_pretrained("gnm-t5")

data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model, return_tensors="tf")

print("\n🧪 Testuojame modelį su keliomis ivestimis:\n")
for i in range(3):
    tekstas = test_df.iloc[i]["input"]
    tikras = test_df.iloc[i]["target"]
    input_ids = tokenizer(tekstas, return_tensors="tf", truncation=True, padding=True).input_ids
    output_ids = model.generate(input_ids, max_length=128)
    sugeneruota = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    
    print(f"🔹 Įvestis: {tekstas}")
    print(f"✅ Tikras atsakymas: {tikras}")
    print(f"🧠 Modelio atsakymas: {sugeneruota}\n")



plt.plot(history.history["loss"], label="Train Loss")
plt.plot(history.history["val_loss"], label="Validation Loss")
plt.legend()
plt.title("T5 treniravimo kreivė")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.show()