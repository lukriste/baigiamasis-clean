import pandas as pd
import re
import transformers
import datasets
import sklearn
import matplotlib
import tensorflow as tf
from sqlalchemy import create_engine
from transformers import T5Tokenizer, T5Config, TFAutoModelForSeq2SeqLM
from datasets import Dataset
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

# Spausdiname versijas
print(f"pandas versija: {pd.__version__}")
print(f"sqlalchemy versija: {create_engine.__module__}")
print(f"transformers versija: {transformers.__version__}")
print(f"datasets versija: {datasets.__version__}")
print(f"scikit-learn versija: {sklearn.__version__}")
print(f"tensorflow versija: {tf.__version__}")
print(f"matplotlib versija: {matplotlib.__version__}")

# Bandome įkelti T5 modelį
tokenizer = T5Tokenizer.from_pretrained("t5-small")
model = TFAutoModelForSeq2SeqLM.from_pretrained("t5-small")
print("Modelis sėkmingai įkeltas!")

