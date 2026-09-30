import streamlit as st

from answer import DISCLAIMER, answer_question

st.set_page_config(page_title="Aura | Epilepsy Research Assistant", page_icon="🧠")

st.title("🧠 Aura")
st.subheader("Cited answers from epilepsy research")
st.caption(
    "Aura answers using only retrieved PubMed abstracts (2015-2025), "
    "with a citation for every claim."
)
st.info(DISCLAIMER)

EXAMPLES = [
    "What drugs treat focal seizures?",
    "Does the ketogenic diet help children with epilepsy?",
    "What is the role of EEG in diagnosing epilepsy?",
]

run_q = None

with st.expander("Try an example question"):
    for ex in EXAMPLES:
        if st.button(ex):
            run_q = ex

with st.form("ask"):
    q = st.text_input("Ask a question about epilepsy research")
    submitted = st.form_submit_button("Ask")

if submitted and q.strip():
    run_q = q.strip()

if run_q:
    st.markdown(f"**Question:** {run_q}")
    with st.spinner("Searching papers and writing an answer..."):
        answer, sources = answer_question(run_q)

    st.subheader("Answer")
    st.write(answer)

    if sources:
        st.subheader("Sources")
        st.markdown(sources.replace("\n", "\n\n"))

st.divider()
st.caption(
    "Built with PubMed, sentence-transformers, ChromaDB, Gemini, and Streamlit. "
    "Answers are generated from a limited set of abstracts and may be incomplete."
)