from openai import OpenAI
from pinecone import Pinecone
import json

# Read the document
with open('hospital_services.txt', 'r') as file:
    document_text = file.read()         

# Split the document into segments (e.g., paragraphs)
segments = document_text.split('\n\n')  # Assuming paragraphs are separated by double newlines
print(f"Type: {type(segments)}")
print(f"length: {len(segments)}")

with open('apikeys.json') as config_file:
    config = json.load(config_file)


openai_api_key = config['openai_key']
pinecone_api_key= config['pinecone_key']

# Ensure the segments list contains only non-empty strings
segments = [segment for segment in segments if segment.strip()]
client = OpenAI(api_key=openai_api_key)
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
        api_key=pinecone_api_key
    )
index_name = 'chatbot'
embedding_dim = len(embeddings[0])

# # Connect to the index
index = pc.Index(index_name)

# Prepare vectors for upsert
vectors = [(str(i), embedding, {"text": segment}) for i, (segment, embedding) in enumerate(zip(segments, embeddings))]
index.upsert(vectors,namespace= "ns1")
