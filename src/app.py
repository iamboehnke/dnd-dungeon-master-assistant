import streamlit as st
from markov_model import MarkovNameGenerator  # adjust import based on your code structure

# Load or initialize your model
model = MarkovNameGenerator()

# For demo: train on your existing NPC names CSV
import pandas as pd
names_df = pd.read_csv("data/npc_names.csv")
names = names_df['name'].tolist()
model.train(names)

st.title("D&D Name Generator")

min_len = st.number_input("Min Length", min_value=1, max_value=20, value=4)
max_len = st.number_input("Max Length", min_value=1, max_value=20, value=14)

if st.button("Generate Name"):
    generated_name = model.generate_name(min_length=min_len, max_length=max_len)
    if generated_name:
        st.success(f"Your generated name: **{generated_name}**")
    else:
        st.error("Failed to generate a name. Try different length values.")
