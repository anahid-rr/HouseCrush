# warning
import warnings

warnings.filterwarnings("ignore")

import os
from dotenv import load_dotenv
from together import Together
import faiss

from sentence_transformers import SentenceTransformer

"""
Do these steps:
1) Set up a Together API key from https://together.ai/
2) Create a .env file in the project root and add your API key:
   TOGETHER_API_KEY=your_api_key_here
"""
# Load environment variables from .env file
load_dotenv()
together_api_key = os.getenv("TOGETHER_API_KEY")

if not together_api_key:
    raise ValueError("TOGETHER_API_KEY not found in .env file. Please add it to your .env file.")

def run_rag(data_dict: dict, prompt: str):
    """
    Run RAG system: process documents, create embeddings, search, and generate answer.

    """

    # Stage 0: Initialize Together AI client for LLM completions
    client = Together(api_key=together_api_key)

    # Stage 1: Load sentence transformer model for creating embeddings
    # ------------------------------------------------------------
    embedding_model = SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2",
        use_auth_token=os.environ.get("HUGGINGFACE_HUB_TOKEN"),
    )

    # Stage 2: Process documents into Vector Database
    # ------------------------------------------------------------
    documents = []
    filenames = []

    print(f"Processing {len(data_dict)} documents...")
    for key, content in data_dict.items():
        content = content.strip()
        if content:  # Only add non-empty documents
            documents.append(content)
            filenames.append(key)
            print(f"✅ Loaded: {key}")

    if not documents:
        return "No valid documents found in data dictionary!"

    # Create embeddings for all documents
    print("Creating embeddings...")
    embeddings = embedding_model.encode(documents)

    # Set up FAISS index for similarity search
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)

    # Normalize embeddings for cosine similarity
    faiss.normalize_L2(embeddings)
    index.add(embeddings)

    print(f"✅ RAG system ready with {len(documents)} documents!")

    # Stage 3: Retrieve relevant documents
    # ------------------------------------------------------------
    query_embedding = embedding_model.encode([prompt])
    faiss.normalize_L2(query_embedding)

    # Get top similar documents
    scores, indices = index.search(query_embedding, min(3, len(documents)))

    # Stage 4: Build context from retrieved documents
    # ------------------------------------------------------------
    relevant_docs = []
    context_parts = []

    for score, idx in zip(scores[0], indices[0]):
        if idx < len(documents):
            doc_info = {
                "content": documents[idx],
                "filename": filenames[idx],
                "score": float(score),
            }
            relevant_docs.append(doc_info)
            context_parts.append(f"[{doc_info['filename']}]\n{doc_info['content']}")

    if not relevant_docs:
        return "No relevant documents found for the query."

    # Combine context
    context = "\n\n".join(context_parts)

    # Stage 5: Augment by running the LLM to generate an answer
    # ------------------------------------------------------------
    llm_prompt = f"""Answer the question based on the provided context documents.

Context:
{context}

Question: {prompt}

Instructions:
- Answer based only on the information in the context
- Answer should beat least 10 words at max 20 words
- If the context doesn't contain enough information, say so
- Mention which document(s) you're referencing
- Start with According to [document name]
- Add brackets to the document name


Answer:"""

    try:
        # Generate answer using Together AI
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
            messages=[{"role": "user", "content": llm_prompt}],
            max_tokens=500,
            temperature=0.7,
        )
        answer = response.choices[0].message.content

        # Display source information
        print(f"\n📚 Most relevant source:")
        for doc in relevant_docs:
            print(f"  • {doc['filename']} (similarity: {doc['score']:.3f})")

        # Add source information to the answer
        sources_list = [doc["filename"] for doc in relevant_docs]
        sources_text = sources_list[0]
        full_answer = f"{answer}\n\n📄 Source Used: {sources_text}"

        return full_answer

    except Exception as e:
        return f"Error generating answer: {str(e)}"


if __name__ == "__main__":

    # Load dataset with rental property information
    data_dict = {
        "downtown_apartments": "Downtown apartments are typically within walking distance to major business districts, restaurants, and entertainment venues. Average rent ranges from $1,800 to $3,500 for 1-2 bedroom units. Most buildings offer amenities like gyms, rooftop terraces, and 24/7 security.",
        "suburban_homes": "Suburban homes offer more space and privacy compared to city apartments. Typical features include 2-4 bedrooms, private yards, and garage parking. Rent ranges from $2,500 to $4,000. These areas are known for good schools and family-friendly environments.",
        "nearby_amenities": "Important amenities to consider: grocery stores (within 1 mile), public transportation (bus/train stops), schools (elementary, middle, high), parks and recreation areas, medical facilities, and shopping centers. These can significantly impact daily convenience and quality of life.",
        "rental_requirements": "Standard rental requirements include: proof of income (3x monthly rent), credit score check (minimum 650), security deposit (1-2 months rent), rental history, and references. Some properties may require additional fees for pets or parking.",
        "property_types": "Common rental property types: studio apartments (400-600 sq ft), 1-bedroom apartments (600-800 sq ft), 2-bedroom apartments (800-1200 sq ft), townhouses (1200-2000 sq ft), and single-family homes (1500-3000 sq ft). Each type offers different space and privacy levels.",
        "location_factors": "Key location factors to consider: commute time to work (ideal: under 30 minutes), distance to public transportation (ideal: under 0.5 miles), neighborhood safety ratings, walkability score, and proximity to essential services like hospitals and schools.",
        "rental_trends": "Current rental market trends show increasing demand for properties with home office spaces, outdoor areas, and energy-efficient features. Properties with smart home technology and high-speed internet infrastructure are particularly sought after."
    }

    question = "What are the typical rental requirements?"
    answer = run_rag(data_dict, question)
    print(f"\n🤖 Answer: {answer}\n")
    print("-" * 50)