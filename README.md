Aura: Epilepsy Research Assistant

Cited answers from epilepsy research. Aura is a retrieval-augmented generation (RAG) assistant that answers epilepsy research questions using only retrieved PubMed abstracts, with a numbered citation and DOI link for every claim.

Live demo: (https://aura-epilepsy-rag-makpukdhvtd77epimes65l.streamlit.app/)

Aura is named after the warning sensation some people feel before a seizure: it surfaces the relevant signals from a large body of research.

## Features

- **Grounded answers:** responses are generated only from retrieved paper abstracts, not from the model's general memory.
- **Citations on every claim:** numbered references linked to the paper's DOI (or PubMed page when no DOI exists).
- **"I don't know" behavior:** if the best match is too far from the question, Aura says it couldn't find the answer instead of guessing.
- **Medical safety guardrail:** personal questions such as "do I have epilepsy?" are declined, and a disclaimer is shown throughout.
- **Simple web interface:** built with Streamlit, with example questions to try.

## Tech stack

| Layer | Tool |
|---|---|
| Language | Python |
| Data source | PubMed E-utilities API |
| Embeddings | `sentence-transformers` (`all-MiniLM-L6-v2`) |
| Vector database | ChromaDB |
| LLM | Google Gemini API (free tier) |
| Interface | Streamlit |
| Hosting | Streamlit Community Cloud |

## Limitations

- **Abstracts only:** Aura reads abstracts, not full papers, so details from methods and results sections are often missing.
- **Limited coverage:** about 1,000 English-language papers from 2015-2025, so it does not cover all epilepsy research.
- **Answers can be generic** when the retrieved papers are reviews rather than detailed studies.
- **Not medical advice:** Aura is for research and education only. It does not diagnose or recommend treatment.
- **Free-tier limits:** the LLM API and hosting are free-tier services, so the demo may be slow or briefly unavailable under heavy use.

## Project structure

```
├── app.py            # Streamlit web interface
├── answer.py         # retrieval, guardrails, and LLM answer generation
├── fetch_papers.py   # PubMed data collection
├── build_index.py    # chunking, embeddings, vector store
├── test_search.py    # test retrieval on its own
├── check_papers.py   # inspect the downloaded data
├── data/             # papers.json
├── chroma_db/        # vector index
└── requirements.txt
```

## Roadmap

- Hybrid search (keyword + semantic) with reranking
- Filters by year and study type, plus evidence-strength labels
- Follow-up questions with conversation memory
- Show only the sources actually cited in the answer

## Data and acknowledgements

Paper metadata and abstracts come from [PubMed](https://pubmed.ncbi.nlm.nih.gov/) via the NCBI E-utilities API. Each answer links back to the original publication.
