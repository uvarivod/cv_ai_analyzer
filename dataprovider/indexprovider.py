from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex

class IndexProvider:
    """
    IndexProvider is responsible for managing the process of loading, storing, and retrieving data
    from ChromaDB in a vector store. It can either load existing data from ChromaDB or store new
    documents by splitting them into chunks and indexing them in the vector store.

    Attributes:
        index (VectorStoreIndex): The index used for storing and querying documents.
        vector_store (ChromaVectorStore): The vector store used to interact with ChromaDB.
        storage_context (StorageContext): The context used for storage operations in the vector store.
    """

    def __init__(self, vector_store, storage_context):
        """
        Initializes the IndexProvider with the given vector store and storage context.

        Args:
            vector_store (ChromaVectorStore): The vector store object to interact with ChromaDB.
            storage_context (StorageContext): The storage context for the index.
        """
        self.index = None
        self.vector_store = vector_store
        self.storage_context = storage_context

    def get_index(self, chroma_collection):
        """
        Retrieves the index. If there are existing filenames in ChromaDB, it loads the index
        from the vector store; otherwise, it loads documents from a directory and stores them
        in ChromaDB.

        Args:
            chroma_collection (ChromaCollection): The ChromaDB collection to check for existing data.

        Returns:
            VectorStoreIndex: The loaded or newly created index.
        """
        if len(self.get_filenames_in_chroma(chroma_collection)) > 0:
            return self.load_data_from_chroma()
        documents = SimpleDirectoryReader("data/AUTOMOBILE").load_data()
        return self.store_data_to_chroma(documents)

    def store_data_to_chroma(self, documents):
        """
        Splits the given documents into chunks and stores them in ChromaDB.

        Each document is split into chunks using a sentence splitter, and the chunks are then
        indexed in the ChromaDB vector store.

        Args:
            documents (list): A list of documents to be stored in ChromaDB.

        Returns:
            VectorStoreIndex: The created index after storing the documents.
        """
        splitter = SentenceSplitter(chunk_size=512, chunk_overlap=100)
        chunks = splitter.get_nodes_from_documents(documents)

        print(f"Split into {len(chunks)} chunks")

        # Create an index with the chunks
        index = VectorStoreIndex(nodes=chunks, storage_context=self.storage_context)
        return index

    def load_data_from_chroma(self):
        """
        Loads the existing data from ChromaDB using the provided vector store and storage context.

        Returns:
            VectorStoreIndex: The loaded index from the ChromaDB vector store.
        """
        return VectorStoreIndex.from_vector_store(self.vector_store, storage_context=self.storage_context)

    def get_filenames_in_chroma(self, chroma_collection):
        """
        Retrieves a list of document filenames from the metadata stored in ChromaDB.

        Args:
            chroma_collection (ChromaCollection): The ChromaDB collection from which to extract metadata.

        Returns:
            list: A list of unique document filenames found in the ChromaDB metadata.
        """
        docs = chroma_collection.get(include=['metadatas'])
        document_ids = []

        if 'metadatas' in docs and docs['metadatas']:
            for metadata in docs['metadatas']:
                if metadata and 'file_name' in metadata:
                    document_ids.append(metadata['file_name'])

        return list(set(document_ids))
