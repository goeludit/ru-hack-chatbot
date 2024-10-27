import openai
import re
# Set your OpenAI API key here

import openai
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from dotenv import load_dotenv
import os

# load_dotenv()

# Now you can access the API key
# api_key = os.getenv("OPENAPI_KEY")
# openai.api_key = api_key

openai.api_key ='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'
# Documents dictionary for example purposes
# Replace with your actual documents, e.g., loaded from files or database
documents = {
    "doc1": "The Hormonal Patch is a pad-based ELISA with iPhone integration. Its components include a  biomaterial-based sticker that can be placed on the interior of a pad, which will absorb menstrual blood. This sticker will react with specific hormone metabolites, such as thyroid hormones, in the menstrual blood, leading to a visible color change. Users can then photograph the color change using a smartphone app to analyze the image and provide insights into hormone levels. ",
    "doc2": "The sticker would be made from the same materials as pads to ensure comfort and familiarity for users while integrating safe, biocompatible chemical reactions that allow for non-invasive hormone monitoring. This innovation could offer a convenient and user-friendly method for tracking hormonal health through menstrual blood."
}

# Step 1: Create Embeddings for Each Document
def create_document_embeddings(documents):
    embeddings = {}
    for doc_id, doc_text in documents.items():
        embedding = openai.Embedding.create(
            input=doc_text,
            model="text-embedding-ada-002"
        )['data'][0]['embedding']
        embeddings[doc_id] = embedding
    return embeddings

# Generate and save embeddings once
def save_embeddings():
    document_embeddings = create_document_embeddings(documents)
    with open("document_embeddings.json", "w") as f:
        json.dump(document_embeddings, f)

# Step 2: Load Embeddings and Retrieve Relevant Document
def load_document_embeddings(file_name="document_embeddings.json"):
    with open(file_name, "r") as f:
        return json.load(f)

def get_relevant_document(query):
    # Load embeddings
    document_embeddings = load_document_embeddings()

    # Get embedding for the user query
    query_embedding = openai.Embedding.create(
        input=query,
        model="text-embedding-ada-002"
    )['data'][0]['embedding']
    
    # Calculate similarity between the query and each document
    similarities = {}
    for doc_id, embedding in document_embeddings.items():
        similarities[doc_id] = cosine_similarity(
            [query_embedding], [np.array(embedding)]
        )[0][0]
    
    # Find the most relevant document
    best_match_id = max(similarities, key=similarities.get)
    return documents[best_match_id]

# Step 3: Generate Response Based on Relevant Document
def get_chatgpt_response(user_message):
    """
    Generates a response from OpenAI's ChatGPT model based on user input,
    using only relevant content from specific documents.
    """
    try:
        if re.search(r"\b(book|appointment|schedule|next steps|doctor)\b", user_message, re.IGNORECASE):
            # Return a response prompting the user to proceed with booking
            return "It sounds like you'd like to book an appointment. Please select a doctor and choose a time."

        # Retrieve the most relevant document
        relevant_text = get_relevant_document(user_message)
        
        # Build the prompt with the relevant document as context
        prompt = f"Context: {relevant_text}\n\nUser: {user_message}\nAssistant:"
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides answers based only on the provided context."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=150,
            temperature=0.7,
        )

        return response['choices'][0]['message']['content'].strip()

    except Exception as e:
        print(f"OpenAI API error: {e}")
        return "I'm sorry, but I'm having trouble connecting to the chatbot service right now."


# Save embeddings once when setting up
# Comment this line after the first run or when documents change
save_embeddings()
