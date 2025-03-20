import chromadb
from dotenv import load_dotenv
from llama_index.core import Settings, StorageContext
from llama_index.llms.groq import Groq
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import get_response_synthesizer
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.vector_stores import MetadataFilter, MetadataFilters, FilterOperator
from llama_index.core.query_engine import RetrieverQueryEngine

from dataprovider.indexprovider import IndexProvider

# Load environment variables from a .env file
load_dotenv()

# Setup LLM (Language Learning Model) and embeddings for text analysis
Settings.llm = Groq(model="gemma2-9b-it")
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

# Initialize Chroma client and collection for persistent vector storage
db = chromadb.PersistentClient(path="./chromadb")
chroma_collection = db.get_or_create_collection("CVs")
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

index_provider = IndexProvider(vector_store, storage_context)


def create_retriever_for_file_in_chromadb(file_name, index):
    """
    Creates a retriever for a specific file in the Chroma database with a metadata filter.

    Args:
        file_name (str): The name of the file to retrieve.
        index: The index to be used for retrieval.

    Returns:
        retriever: The retriever object that will fetch the file with the given metadata filter.
    """
    filters = MetadataFilters(
        filters=[
            MetadataFilter(key="file_name", operator=FilterOperator.EQ, value=file_name),
        ]
    )
    retriever = index.as_retriever(filters=filters)
    return retriever


def get_json_for_stored_file(filename, index):
    """
    Retrieves and analyzes a stored file from Chroma, returning a JSON object with the analysis.

    Args:
        filename (str): The name of the file to retrieve and analyze.
        index: The index to be used for retrieving the file.

    Returns:
        dict: The JSON response containing the analysis of the CV document.
    """
    retr = create_retriever_for_file_in_chromadb(filename, index)
    response_synthesizer = get_response_synthesizer()

    query_engine = RetrieverQueryEngine(
        retriever=retr,
        response_synthesizer=response_synthesizer,
        node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.0)]
    )

    # Define the prompt template to analyze the CV document
    prompt = """
    [INST]

    <<SYS>>
        You are a Recruiter, experienced in CV analyzing
    <</SYS>>
    You will be provided with CV document. Your task to make json file with analyzed document.
    Document should have keys: 
    'profession' - profession from document, 
    'years' - sum of years of commercial experience found in document
    'summary' - summary of candidate (up to 3 sentences)
    'strongest_skills' - strongest skills found in document
    'challenges' - professional highlights found in Document
    
    Prepare CSV {'profession':...
    ...
    
    Double check your output that it does not contain ```json ``` as enclosures 
       Output:

                Provide the content of a single JSON file that has keys for every document
                !!! Provide only the generated json enclosed in {}. Do not add any additional symbols to it, including markdown.
                !!! Output will be directly used in parsing so do not even add ```json ``` 
                Output should be ready for parsing without postprocessing
    [/INST]
    """

    # Get response from the query engine
    response = query_engine.query(prompt)
    return response


def analyze_cvs():
    """
    Analyzes all CVs stored in the Chroma collection and returns a list of candidate analyses.

    Returns:
        list: A list of JSON responses with the analysis of each CV document.
    """
    index = index_provider.get_index(chroma_collection)

    # Get all filenames stored in Chroma collection
    files_in_chroma = index_provider.get_filenames_in_chroma(chroma_collection)
    candidates = []

    # For each file, retrieve and analyze the CV document
    for each in files_in_chroma:
        candidate = get_json_for_stored_file(each, index)
        print(candidate)
        candidate_json = candidate.response
        start = candidate_json.find('{')
        end = candidate_json.rfind('}')

        if start == -1 or end == -1 or start > end:
            json_obj = '{}'
        else:
            json_obj = candidate_json[start:end + 1]

        candidates.append(json_obj)

    return candidates


if __name__ == '__main__':
    # Main entry point to analyze CVs and print the results
    cands = analyze_cvs()
    print(cands)
