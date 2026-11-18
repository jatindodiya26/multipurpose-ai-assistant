import os
import uuid

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma


VECTORSTORE_PATH = "vectorstore"


# --------------------------------------------------
# Create Embeddings
# --------------------------------------------------

def get_embeddings():

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    return embeddings


# --------------------------------------------------
# Get Existing Vector Store
# --------------------------------------------------

def get_vectorstore():

    embeddings = get_embeddings()

    vectorstore = Chroma(
        persist_directory=VECTORSTORE_PATH,
        embedding_function=embeddings
    )

    return vectorstore


# --------------------------------------------------
# Add PDF to Vector Store
# --------------------------------------------------

# --------------------------------------------------
# Add PDF to Vector Store
# --------------------------------------------------

def add_pdf_to_vectorstore(
    pdf_path,
    pdf_name,
    user_id=None
):

    if user_id is None:
         user_id = 0
         
    # Create unique document ID
    document_id = str(uuid.uuid4())

    # Load PDF
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    # Check whether PDF contains text
    valid_documents = []

    for document in documents:

        if document.page_content.strip():

            document.metadata["source"] = pdf_name
            document.metadata["document_id"] = document_id
            document.metadata["user_id"] = user_id

            valid_documents.append(document)

    # Stop if no text was extracted
    if not valid_documents:
        raise ValueError(
            f"No readable text was found in '{pdf_name}'. "
            "This PDF may be scanned/image-based or empty."
        )

    # Split document
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = text_splitter.split_documents(
        valid_documents
    )

    # Remove empty chunks
    chunks = [
        chunk
        for chunk in chunks
        if chunk.page_content.strip()
    ]

    # Check chunks
    if not chunks:
        raise ValueError(
            f"No text chunks could be created from "
            f"'{pdf_name}'."
        )

    # Create embeddings
    embeddings = get_embeddings()

    # Open vectorstore
    vectorstore = Chroma(
        persist_directory=VECTORSTORE_PATH,
        embedding_function=embeddings
    )

    # Add documents
    vectorstore.add_documents(
        chunks
    )

    return (
        vectorstore,
        len(valid_documents),
        len(chunks),
        document_id
    )


# --------------------------------------------------
# Search PDFs
# --------------------------------------------------

def search_pdf(query: str, user_id: int):
    try:
        if not os.path.exists(VECTORSTORE_PATH):
            return (
                "No PDF has been uploaded and processed yet."
            )

        vectorstore = get_vectorstore()

        documents = vectorstore.similarity_search(
            query,
            k=5,
            filter={
                "user_id": user_id
            }
        )

        if not documents:
            return (
                "No relevant information was found "
                "in your uploaded PDFs."
            )

        results = []

        for document in documents:
            source = document.metadata.get(
                "source",
                "Unknown PDF"
            )

            page = document.metadata.get(
                "page",
                "Unknown"
            )

            if isinstance(page, int):
                page = page + 1

            results.append(
                f"Source: {source}\n"
                f"Page: {page}\n"
                f"Content:\n{document.page_content}"
            )

        return "\n\n---\n\n".join(results)

    except Exception as e:
        return (
            f"Unable to search the uploaded PDFs: "
            f"{str(e)}"
        )

# --------------------------------------------------
# Delete PDF
# --------------------------------------------------


def delete_pdf(pdf_name: str, user_id: int):
    try:
        if not os.path.exists(VECTORSTORE_PATH):
            return False, "Vectorstore does not exist."

        vectorstore = get_vectorstore()

        collection = vectorstore._collection

        results = collection.get(
            where={
                "$and": [
                    {"source": pdf_name},
                    {"user_id": user_id}
                ]
            },
            include=["metadatas"]
        )

        ids = results.get("ids", [])

        if not ids:
            return (
                False,
                f"No PDF named '{pdf_name}' belongs "
                f"to your account."
            )

        collection.delete(ids=ids)

        return (
            True,
            f"Deleted {len(ids)} chunks belonging "
            f"to {pdf_name}."
        )

    except Exception as e:
        return False, f"Failed to delete PDF: {str(e)}"


def get_user_pdfs(user_id: int):
    try:
        if not os.path.exists(VECTORSTORE_PATH):
            return []

        vectorstore = get_vectorstore()

        results = vectorstore._collection.get(
            where={"user_id": user_id},
            include=["metadatas"]
        )

        pdf_names = set()

        for metadata in results["metadatas"]:
            source = metadata.get("source")

            if source:
                pdf_names.add(source)

        return sorted(pdf_names)

    except Exception as e:
        print(f"Failed to retrieve user PDFs: {e}")
        return []
