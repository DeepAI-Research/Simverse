import os
import json
import chromadb
from chromadb.utils import embedding_functions
from rich.progress import Progress, TextColumn, BarColumn, TimeRemainingColumn, MofNCompleteColumn
from rich.console import Console
from rich.panel import Panel
from sentence_transformers import SentenceTransformer
from chromadb.config import Settings


def initialize_chroma_db():
    db_path = "./chroma_db"
    
    # Check if the database directory exists
    if not os.path.exists(db_path):
        print("Database not found. Creating new database.")
        os.makedirs(db_path)
    
    # Initialize Chroma client
    chroma_client = chromadb.PersistentClient(path=db_path, settings=Settings(anonymized_telemetry=False))

    # Create or get collections for each data type
    object_collection = chroma_client.get_or_create_collection(name="object_captions")
    hdri_collection = chroma_client.get_or_create_collection(name="hdri_backgrounds")
    texture_collection = chroma_client.get_or_create_collection(name="textures")

    # Process collections if they are empty
    def process_if_empty(collection, file_path, description):
        if collection.count() == 0:
            if os.path.exists(file_path):
                print(f"Processing {description}...")
                process_in_batches(file_path, collection, batch_size=1000)
            else:
                print(f"File not found: {file_path}. Please check the file path.")
        else:
            print(f"{description} already processed. Skipping.")

    # Adjusted paths to reflect the correct location of the datasets folder
    datasets_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../datasets"))

    process_if_empty(object_collection, os.path.join(datasets_path, 'cap3d_captions.json'), "object captions")
    process_if_empty(hdri_collection, os.path.join(datasets_path, 'hdri_data.json'), "HDRI backgrounds")
    process_if_empty(texture_collection, os.path.join(datasets_path, 'texture_data.json'), "textures")

    # Check if collections are empty and process data if needed
    if object_collection.count() == 0:
        print("Processing object captions...")
        process_in_batches('../datasets/cap3d_captions.json', object_collection, batch_size=1000)
    else:
        print("Object captions already processed. Skipping.")

    if hdri_collection.count() == 0:
        print("Processing HDRI backgrounds...")
        process_in_batches('../datasets/hdri_data.json', hdri_collection, batch_size=1000)
    else:
        print("HDRI backgrounds already processed. Skipping.")

    if texture_collection.count() == 0:
        print("Processing textures...")
        process_in_batches('../datasets/texture_data.json', texture_collection, batch_size=1000)
    else:
        print("Textures already processed. Skipping.")

    print("Database initialization complete.")

    return chroma_client


# Function to process data in batches
def process_in_batches(file_path, collection, batch_size=1000):
    model = SentenceTransformer('all-MiniLM-L6-v2')  # or another appropriate model

    # Create the embedding function
    sentence_transformer_ef = model.encode
    # Create the embedding function
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name='all-MiniLM-L6-v2')

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


# Function to query a single collection
def query_collection(sentence_transformer_ef, query, collection, n_results=2):
    console = Console()
    query_embedding = sentence_transformer_ef([query])
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results
    )
    console.print(Panel(str(results), title=f"Query Results for {collection.name}", expand=False))
    return results


# Optional: You can still combine results if needed
def combine_results(object_results, hdri_results, texture_results):
    # This is a placeholder function. Implement the logic to combine results based on your needs.
    combined_results = {
        "object_captions": object_results,
        "hdri_backgrounds": hdri_results,
        "textures": texture_results
    }
    return combined_results