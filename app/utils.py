# --- app/utils.py ---
import os
import openai
import numpy as np

openai.api_key = os.getenv("OPENAI_API_KEY")
openai_client = openai.Client(
    api_key=os.getenv("OPENAI_API_KEY"),
    max_retries=20,
    )

def get_embedding(text: str) -> list:
    response = openai_client.embeddings.create(
        input=text,
        model="text-embedding-3-small",
    )
    return response.data[0].embedding

def cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def get_top_k_chunks(query: str, chunks: list, k=5):
    query_emb = get_embedding(query)
    ranked = sorted(
        chunks,
        key=lambda x: cosine_similarity(query_emb, x['embedding']),
        reverse=True
    )
    return ranked[:k]

def call_openai_with_context(question, context):
    prompt = f"""
    You are a codebase assistant. Use the context below to answer the user question.

    [Context Start]
    {context}
    [Context End]

    Question: {question}
    Answer:
    """
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()
