"""
    create db just from online collection (qdrant)
"""
import os
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_experimental.text_splitter import SemanticChunker
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from tqdm import tqdm
import pandas as pd
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from dotenv import load_dotenv
from db_manager import DBManager, init_db

# add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from config import IndexConfig
from data_processing.data_utils import load_data
load_dotenv()

QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

def main():
    cfg = IndexConfig()
    papers_df, paper_authors, paper_references = load_data(drop_missing=cfg.drop_missing)
    init_db(clear=True)
    db_manager = DBManager()
    print("Indexing papers...")
    print(f"Number of papers: {len(papers_df)}")

    for index, row in tqdm(papers_df.iterrows(), total=len(papers_df)):
        arxiv_id = row["arxiv_id"]
        semantic_scholar_id = row["semantic_scholar_id"]
        # Get authors and references
        authors = paper_authors.get(arxiv_id, [])
        references = paper_references.get(arxiv_id, [])

        # Insert into PostgreSQL using the DBManager
        db_manager.insert_paper(
            arxiv_id=str(arxiv_id),
            semantic_scholar_id=str(semantic_scholar_id),
            title=str(row["title"]),
            super_category=str(row["super_category"]),
            update_year=int(row["update_year"]),
            reference_count=int(row["reference_count"]),
            citation_count=int(row["citation_count"]),
            author_count=int(row["author_count"]),
            authors=authors,
            references=references
        )

    print("Finished indexing papers!")
    db_manager.close()

if __name__ == "__main__":
    main()
