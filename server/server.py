import json
import chromadb
from chromadb.utils import embedding_functions
from rich.progress import Progress, TextColumn, BarColumn, TimeRemainingColumn, MofNCompleteColumn
from rich.console import Console
from rich.panel import Panel

# Initialize Chroma client
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Initialize the embedding function using Sentence Transformers
sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# Create or get collections for each data type
object_collection = chroma_client.get_or_create_collection(name="object_captions")
hdri_collection = chroma_client.get_or_create_collection(name="hdri_backgrounds")
texture_collection = chroma_client.get_or_create_collection(name="textures")

# Function to process data in batches
def process_in_batches(file_path, collection, batch_size=1000):
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
        task = progress.add_task(f"[green]Processing {file_path}", total=total_items, current_batch="0")

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

    console.print(Panel.fit(f"Data processing complete for {file_path}!", border_style="green"))

# Process each data type
# process_in_batches('./datasets/cap3d_captions.json', object_collection, batch_size=1000)
# process_in_batches('./datasets/hdri_data.json', hdri_collection, batch_size=1000)
# process_in_batches('./datasets/texture_data.json', texture_collection, batch_size=1000)

# Function to query a single collection
def query_collection(query, collection, n_results=2):
    console = Console()
    query_embedding = sentence_transformer_ef([query])
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results
    )
    console.print(Panel(str(results), title=f"Query Results for {collection.name}", expand=False))
    return results

# Example usage
console = Console()
query = "A person is playing the guitar in a studio."

console.print(Panel("Querying Object Captions Collection", style="bold magenta"))
object_results = query_collection(query, object_collection, n_results=2)

console.print(Panel("Querying HDRI Backgrounds Collection", style="bold cyan"))
hdri_results = query_collection(query, hdri_collection, n_results=2)

console.print(Panel("Querying Textures Collection", style="bold green"))
texture_results = query_collection(query, texture_collection, n_results=2)

# Optional: You can still combine results if needed
def combine_results(object_results, hdri_results, texture_results):
    # This is a placeholder function. Implement the logic to combine results based on your needs.
    combined_results = {
        "object_captions": object_results,
        "hdri_backgrounds": hdri_results,
        "textures": texture_results
    }
    return combined_results

combined_results = combine_results(object_results, hdri_results, texture_results)
console.print(Panel(str(combined_results), title="Combined Query Results", expand=False))

# # Main execution
# if __name__ == "__main__":
#     console.print(Panel("Chroma Database Query System", style="bold blue"))
#     while True:
#         user_query = console.input("[bold yellow]Enter your query (or 'quit' to exit): ")
#         if user_query.lower() == 'quit':
#             break
        
#         console.print(Panel("Querying Object Captions Collection", style="bold magenta"))
#         query_collection(user_query, object_collection, n_results=2)
        
#         console.print(Panel("Querying HDRI Backgrounds Collection", style="bold cyan"))
#         query_collection(user_query, hdri_collection, n_results=2)
        
#         console.print(Panel("Querying Textures Collection", style="bold green"))
#         query_collection(user_query, texture_collection, n_results=2)