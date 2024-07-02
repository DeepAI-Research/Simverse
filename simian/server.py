import json
import chromadb

# Load the JSON file
with open('./datasets/cap3d_captions.json', 'r') as file:
    data = json.load(file)

# Extract IDs and documents
ids = list(data.keys())
documents = list(data.values())

print("These are the IDs:", ids)
print("These are the documents:", documents)

# Initialize ChromaDB client and collection
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="simversedb")

# Upsert documents into the collection
collection.upsert(
    documents=documents,
    ids=ids
)

# Verify the upsert
results = collection.query(
    query_texts=["A query document example"], # Change this to your actual query
    n_results=2 # Number of results to return
)

print(results)
