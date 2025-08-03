# Basic solution - RAG only

embed each python component by ast:
embedding = get_embedding(snippet)
get best k components by cosine_similarity
"bleu_score": {
"mean": 0.08772979728506276,
"median": 0.10490317245658279,
"std": 0.06084255475853148,
"min": 0.007267274044312383,
"max": 0.1541570776538462
}

# Basic solution - FastMCP, langchain, langgraph
"bleu_score": {
"mean": 0.09645719334514223,
"median": 0.08256016752515546,
"std": 0.10059506852145292,
"min": 0.000925222205178214,
"max": 0.3263051344690725
}

