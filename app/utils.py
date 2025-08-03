# --- app/utils.py ---
import os
import openai
import numpy as np
from typing import List, Dict

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


def get_top_k_chunks(query: str, chunks: List[Dict], k=5):
    query_emb = get_embedding(query)
    
    # Compute similarity for each chunk and store it
    similarities = []
    for chunk in chunks:
        sim = cosine_similarity(query_emb, chunk['embedding'])
        similarities.append({
            'content': chunk["content"],
            'similarity': sim
        })
    
    # Sort by similarity in descending order
    ranked = sorted(similarities, key=lambda x: x['similarity'], reverse=True)
    
    # Return top-k results with similarity scores
    return ranked[:k]
    
def call_openai_with_context(question, context_list, context_length=3000):
    def count_words(text):
        return len(text.strip().split(" "))

    # Build the fixed parts of the prompt
    intro = """
    You are a codebase assistant. Use the context below to answer the user question.

    [Context Start]
    """
    
    context_end_and_question = f"""
    [Context End]

    Question: {question}
    Answer:
    """

    # Word count for fixed parts (excluding the dynamic context)
    fixed_word_count = count_words(intro) + count_words(context_end_and_question)
    
    # Space available for context content
    available_words_for_context = context_length - fixed_word_count

    if available_words_for_context <= 0:
        raise ValueError("Context length is too small to fit even the fixed parts of the prompt.")

    # Add contexts until we exceed the word budget
    selected_contexts = []
    used_words = 0

    for ctx in context_list:
        ctx_words = count_words(ctx)
        # Each context after the first adds a separator "\n\n", which doesn't add words
        # So we just count the words in the context itself
        if used_words + ctx_words <= available_words_for_context:
            selected_contexts.append(ctx)
            used_words += ctx_words
        else:
            break  # No more contexts can fit

    if len(selected_contexts) == 0:
        warning_message = "No context was found for the question. Please try again with a different question."
        print(warning_message)
    # Construct the final prompt
    context_str = "\n\n".join(selected_contexts)
    prompt = f"""
    You are a codebase assistant. Use the context below to answer the user question.

    [Context Start]
    {context_str}
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