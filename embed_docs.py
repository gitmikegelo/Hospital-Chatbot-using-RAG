from openai import OpenAI
from pinecone import Pinecone

# Read the document
with open('hospital_services.txt', 'r') as file:
    document_text = file.read()         

# Split the document into segments (e.g., paragraphs)
segments = document_text.split('\n\n')  # Assuming paragraphs are separated by double newlines
print(f"Type: {type(segments)}")
print(f"length: {len(segments)}")

# Ensure the segments list contains only non-empty strings
segments = [segment for segment in segments if segment.strip()]
client = OpenAI(api_key="sk-proj-zHDvcO8W8yQIyqGBri5vT3BlbkFJ90kqaOxHlBJbFM8tXfm7")
response = client.embeddings.create(
    model="text-embedding-ada-002",
    input=segments
)   

print(response)
# Extract embeddings
# Extract embeddings from the response object
embeddings = [embedding.embedding for embedding in response.data]

print(response)
# Extract embeddings
# Extract embeddings from the response object
embeddings = [embedding.embedding for embedding in response.data]


pc = Pinecone(
        api_key="305eba2c-b5fc-4963-bd19-30e0bb4f06c3"
    )
index_name = 'chatbot'
embedding_dim = len(embeddings[0])

# # Connect to the index
index = pc.Index(index_name)

# Prepare vectors for upsert
vectors = [(str(i), embedding, {"text": segment}) for i, (segment, embedding) in enumerate(zip(segments, embeddings))]
index.upsert(vectors,namespace= "ns1")
