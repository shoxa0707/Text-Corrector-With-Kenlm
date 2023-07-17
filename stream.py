import kenlm
import streamlit as st
from lm import *

# load and prepare model to correct words
model = kenlm.LanguageModel("language_model/airi.bin")
model.vocab = prepare_unigram_set("language_model/airi.arpa", model)

st.header("Text corrector")
# Store the initial value of widgets in session state
st.session_state.visibility = "visible"
st.session_state.disabled = False

col1, col2 = st.columns(2)

with col1:
    st.write("Your input sentence:")
    input_sentence = st.text_area(
        label="Enter sentence",
        height=200
    )
    if input_sentence:
        with col2:
            st.write("Corrected sentence:")
            st.session_state.disabled = True
            text_input = st.text_area(
                label="result",
                value=recycle_sentence(model, input_sentence),
                label_visibility=st.session_state.visibility,
                disabled=st.session_state.disabled,
                height=200
            )
    