import os
import json
import chromadb
from chromadb.utils import embedding_functions
from rich.progress import Progress, TextColumn, BarColumn, TimeRemainingColumn, MofNCompleteColumn
from rich.console import Console
from rich.panel import Panel
from sentence_transformers import SentenceTransformer
from chromadb.config import Settings


def initialize_chroma_db(reset_hdri=False, reset_textures=False):
    """
    Initialize the Chroma database with the provided data files.

    Args:
        reset_hdri (bool): Whether to reset and reprocess the HDRI backgrounds.
        reset_textures (bool): Whether to reset and reprocess the textures.

    Returns:
        chroma_client (chromadb.PersistentClient): The initialized Chroma client.
    """
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

    def reset_and_process(collection, file_path, description):
        print(f"Resetting and reprocessing {description}...")
        # Get all IDs in the collection
        all_ids = collection.get(include=['embeddings'])['ids']
        if all_ids:
            # Delete all documents if there are any
            collection.delete(ids=all_ids)
        # Process the data
        process_in_batches(file_path, collection, batch_size=1000)
        
     # Reset and reprocess HDRI if requested
    if reset_hdri:
        reset_and_process(hdri_collection, os.path.join(datasets_path, 'hdri_data.json'), "HDRI backgrounds")
    elif hdri_collection.count() == 0:
        process_in_batches(os.path.join(datasets_path, 'hdri_data.json'), hdri_collection, batch_size=1000)

    # Reset and reprocess textures if requested
    if reset_textures:
        reset_and_process(texture_collection, os.path.join(datasets_path, 'texture_data.json'), "textures")
    elif texture_collection.count() == 0:
        process_in_batches(os.path.join(datasets_path, 'texture_data.json'), texture_collection, batch_size=1000)

    process_if_empty(object_collection, os.path.join(datasets_path, 'cap3d_captions.json'), "object captions")
    process_if_empty(hdri_collection, os.path.join(datasets_path, 'hdri_data.json'), "HDRI backgrounds")
    process_if_empty(texture_collection, os.path.join(datasets_path, 'texture_data.json'), "textures")

    # Check if collections are empty and process data if needed
    if object_collection.count() == 0:
        print("Processing object captions...")
        process_in_batches_objects('../datasets/cap3d_captions.json', object_collection, batch_size=1000)
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


def process_in_batches_objects(file_path, collection, batch_size=1000):
    """
    Process the data in the specified file in batches and upsert it into the collection for objects.

    Args:
        file_path (str): The path to the file containing the data.
        collection (chromadb.Collection): The collection to upsert the data into.
        batch_size (int): The size of each batch for processing.
    
    Returns:
        None
    """
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


def process_in_batches(file_path, collection, batch_size=1000):
    """
    Process the data in the specified file in batches and upsert it into the collection.

    Args:
        file_path (str): The path to the file containing the data.
        collection (chromadb.Collection): The collection to upsert the data into.
        batch_size (int): The size of each batch for processing.
    
    Returns:
        None
    """
    
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name='all-MiniLM-L6-v2')

    console = Console()
    
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    all_ids = list(data.keys())
    total_items = len(all_ids)

    def convert_to_chroma_compatible(value):
        if isinstance(value, (str, int, float, bool)):
            return value
        elif isinstance(value, list):
            return ', '.join(map(str, value))
        elif isinstance(value, dict):
            return json.dumps(value)
        else:
            return str(value)

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
            batch_documents = []
            batch_metadatas = []
            
            for id in batch_ids:
                item = data[id]
                if isinstance(item, str):
                    # For object captions, keep as is
                    batch_documents.append(item)
                    batch_metadatas.append(None)
                else:
                    # For HDRIs and textures
                    name = item.get('name', id)
                    categories = ' '.join(item.get('categories', []))
                    tags = ' '.join(item.get('tags', []))
                    
                    # Create a searchable document string
                    document = f"{name} {categories} {tags}".strip()
                    batch_documents.append(document)
                    
                    # Convert metadata to Chroma-compatible format
                    compatible_metadata = {k: convert_to_chroma_compatible(v) for k, v in item.items()}
                    batch_metadatas.append(compatible_metadata)
            
            # Compute embeddings for the batch using the embedding function
            embeddings = sentence_transformer_ef(batch_documents)
            
            # Upsert the batch into the collection
            collection.upsert(
                ids=batch_ids,
                embeddings=embeddings,
                documents=batch_documents,
                metadatas=batch_metadatas
            )

            # Update progress
            progress.update(task, advance=len(batch_ids), current_batch=f"{i+1}-{min(i+batch_size, total_items)}")

    console.print(Panel.fit(f"Data processing complete for {file_path}!", border_style="green"))


def query_collection(query, sentence_transformer_ef, collection, n_results=2):
    """
    Query the specified collection with the given query and display the results.

    Args:
        query (str): The query string to search for.
        sentence_transformer_ef (embedding_functions.SentenceTransformerEmbeddingFunction): The SentenceTransformer embedding function.
        collection (chromadb.Collection): The collection to query.
        n_results (int): The number of results to display.
    
    Returns:
        dict: The query results.
    """

    console = Console()
    query_embedding = sentence_transformer_ef([query])
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results,
        include=["metadatas", "documents", "distances"]
    )
    
    def parse_metadata_value(value):
        if isinstance(value, str):
            if value.startswith('[') and value.endswith(']'):
                return value.strip('[]').split(', ')
            elif value.startswith('{') and value.endswith('}'):
                return json.loads(value)
        return value

    # Parse the metadata values
    for i, metadata in enumerate(results['metadatas'][0]):
        if metadata:
            results['metadatas'][0][i] = {k: parse_metadata_value(v) for k, v in metadata.items()}
    
    console.print(Panel(str(results), title=f"Query Results for {collection.name}", expand=False))
    return results