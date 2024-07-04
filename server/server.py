import json
import chromadb
from chromadb.utils import embedding_functions
from rich.progress import Progress, TextColumn, BarColumn, TimeRemainingColumn, MofNCompleteColumn
from rich.console import Console
from rich.panel import Panel

# New client initialization
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Create or get the collection
collection = chroma_client.get_or_create_collection(name="simversedb")

# Initialize the embedding function using Sentence Transformers
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# Function to process data in batches
def process_in_batches(file_path, batch_size=1000):
    console = Console()
    
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    all_ids = list(data.keys())
    total_items = len(all_ids)

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeRemainingColumn(),
        TextColumn("Batch: {task.fields[current_batch]}"),
        console=console,
        expand=True
    ) as progress:
        task = progress.add_task("[green]Processing batches", total=total_items, current_batch="0")

        for i in range(0, total_items, batch_size):
            batch_ids = all_ids[i:i+batch_size]
            batch_documents = [data[id] for id in batch_ids]
            
            # Compute embeddings for the batch using the embedding function
            embeddings = sentence_transformer_ef(batch_documents)
            
            # Upsert the batch into the collection
            collection.upsert(
                ids=batch_ids,
                embeddings=embeddings,
                documents=batch_documents
            )

            # Update progress
            progress.update(task, advance=len(batch_ids), current_batch=f"{i+1}-{min(i+batch_size, total_items)}")

    console.print(Panel.fit("Data processing complete!", border_style="green"))

# # Process the data
# process_in_batches('./datasets/cap3d_captions.json', batch_size=1000)

# Verify the upsert by querying
console = Console()
query = "A person is playing the guitar."
query_embedding = sentence_transformer_ef([query])
results = collection.query(
    query_embeddings=query_embedding,
    n_results=2  # Number of results to return
)
console.print(Panel(str(results), title="Query Results", expand=False))