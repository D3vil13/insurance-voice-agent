#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Ingestion Script for Voice Agent
Populates ChromaDB with insurance documents from PDFs and web sources
"""
import sys
import io

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import os
import chromadb
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import fitz  # PyMuPDF
import requests
import tempfile
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

# Use the same database path as the voice agent
DB_PATH = "c:/Users/d3vsh/Downloads/backupMH/chroma_insurance_db"
EMBEDDER_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

print("="*70)
print("INSURANCE DOCUMENT INGESTION")
print("="*70)

# Initialize Chroma persistent DB
print(f"\n📁 Connecting to ChromaDB at: {DB_PATH}")
client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_or_create_collection(name="insurance_docs")

# Check current count
current_count = collection.count()
print(f"✓ Current document count: {current_count}")

# Initialize embedder
print(f"\n🔧 Loading embedder: {EMBEDDER_MODEL}")
embedder = HuggingFaceEmbeddings(model_name=EMBEDDER_MODEL)
print("✓ Embedder loaded")

# Text splitter for chunking
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)


# ========== PDF PROCESSING ==========

def extract_text_from_pdf(pdf_path):
    """Extract text from a local PDF file"""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def extract_text_from_pdf_bytes(pdf_bytes):
    """Extract text from PDF bytes"""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
        tmp_pdf.write(pdf_bytes)
        tmp_pdf_path = tmp_pdf.name

    doc = fitz.open(tmp_pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    os.unlink(tmp_pdf_path)
    return text


def load_local_pdfs():
    """Load PDFs from local directory"""
    print("\n" + "="*70)
    print("LOADING LOCAL PDFs")
    print("="*70)
    
    pdf_files = {
        "FAQs-1": "C:\\Users\\d3vsh\\Downloads\\api\\vectordata_pdf\\FAQs 1.pdf",
        "FAQs-2": "C:\\Users\\d3vsh\\Downloads\\api\\vectordata_pdf\\FAQs 2.pdf",
        "Dialogue-1": "C:\\Users\\d3vsh\\Downloads\\api\\vectordata_pdf\\Dialogue 1.pdf",
        "Dialogue-2": "C:\\Users\\d3vsh\\Downloads\\api\\vectordata_pdf\\Dialogue 2.pdf"
    }
    
    raw_docs = []
    for doc_id, path in pdf_files.items():
        if not os.path.exists(path):
            print(f"⚠️  File not found: {path}")
            continue
            
        try:
            print(f"\n📄 Processing: {doc_id}")
            text_content = extract_text_from_pdf(path)
            doc_type = "faq" if "FAQ" in doc_id else "dialogue"
            raw_docs.append({
                "id": doc_id,
                "text": text_content,
                "type": doc_type
            })
            print(f"✓ Extracted {len(text_content)} characters")
        except Exception as e:
            print(f"❌ Error processing {doc_id}: {e}")
    
    # Chunk and add to database
    if raw_docs:
        print(f"\n🔪 Chunking {len(raw_docs)} documents...")
        docs_added = 0
        
        for doc in raw_docs:
            chunks = text_splitter.split_text(doc["text"])
            print(f"  {doc['id']}: {len(chunks)} chunks")
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc['id']}_chunk{i}"
                emb = embedder.embed_query(chunk)
                
                collection.add(
                    ids=[chunk_id],
                    embeddings=[emb],
                    metadatas=[{
                        "type": doc["type"],
                        "source_doc": doc["id"],
                        "chunk_index": i
                    }],
                    documents=[chunk]
                )
                docs_added += 1
        
        print(f"\n✓ Added {docs_added} document chunks from local PDFs")
    else:
        print("\n⚠️  No local PDFs found")


# ========== WEB SCRAPING ==========

def fetch_page_content_sync(url):
    """Fetch webpage content using synchronous Playwright"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle", timeout=30000)
        content = page.content()
        browser.close()
    return content


def download_pdf(url):
    """Download PDF from URL"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.content


def add_docs_from_url(url):
    """Add documents from URL (PDF or webpage) to ChromaDB"""
    print(f"\n🌐 Processing: {url[:80]}...")
    
    if url.lower().endswith(".pdf") or ".pdf" in url.lower():
        # Download and extract PDF text
        try:
            pdf_bytes = download_pdf(url)
            text = extract_text_from_pdf_bytes(pdf_bytes)
            
            # Chunk the PDF
            chunks = text_splitter.split_text(text)
            print(f"  📄 PDF: {len(chunks)} chunks")
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"web_pdf_{hash(url)}_{i}"
                emb = embedder.embed_query(chunk)
                collection.add(
                    ids=[chunk_id],
                    embeddings=[emb],
                    documents=[chunk],
                    metadatas=[{"source": url, "chunk_index": i, "type": "web_pdf"}]
                )
            
            print(f"  ✓ Added {len(chunks)} chunks from PDF")
        except Exception as e:
            print(f"  ❌ Error processing PDF: {e}")
    else:
        # For webpages, fetch HTML content
        try:
            content = fetch_page_content_sync(url)
            
            # Extract visible text using BeautifulSoup
            soup = BeautifulSoup(content, "html.parser")
            visible_text = soup.get_text(separator="\n", strip=True)
            
            # Chunk the webpage
            chunks = text_splitter.split_text(visible_text)
            print(f"  🌐 Webpage: {len(chunks)} chunks")
            
            for i, chunk in enumerate(chunks):
                chunk_id = f"web_page_{hash(url)}_{i}"
                emb = embedder.embed_query(chunk)
                collection.add(
                    ids=[chunk_id],
                    embeddings=[emb],
                    documents=[chunk],
                    metadatas=[{"source": url, "chunk_index": i, "type": "web_page"}]
                )
            
            print(f"  ✓ Added {len(chunks)} chunks from webpage")
        except Exception as e:
            print(f"  ❌ Error processing webpage: {e}")


def load_web_sources():
    """Load documents from web URLs"""
    print("\n" + "="*70)
    print("LOADING WEB SOURCES")
    print("="*70)
    
    urls = [
        "https://www.icicilombard.com/info-center/faqs",
        "https://www.icicilombard.com/motor-insurance/two-wheeler-insurance",
        "https://www.icicilombard.com/docs/default-source/default-document-library/private-car-package-policy-wording.pdf",
        "https://www.icicilombard.com/docs/default-source/default-document-library/policy-for-protection-of-policyholder.pdf",
        "https://taxguru.in/corporate-law/master-circular-regarding-motor-insurance-products.html"
    ]
    
    for url in urls:
        add_docs_from_url(url)


# ========== MAIN ==========

def main():
    """Main ingestion function"""
    print("\n📋 Choose ingestion source:")
    print("  1. Local PDFs only")
    print("  2. Web sources only")
    print("  3. Both local PDFs and web sources")
    print("  4. Skip ingestion (just check current count)")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        load_local_pdfs()
    elif choice == "2":
        load_web_sources()
    elif choice == "3":
        load_local_pdfs()
        load_web_sources()
    elif choice == "4":
        print("\n⏭️  Skipping ingestion")
    else:
        print("\n❌ Invalid choice")
        return
    
    # Final count
    final_count = collection.count()
    print("\n" + "="*70)
    print("INGESTION COMPLETE")
    print("="*70)
    print(f"📊 Initial count: {current_count}")
    print(f"📊 Final count: {final_count}")
    print(f"📊 Documents added: {final_count - current_count}")
    print(f"\n✓ Database ready at: {DB_PATH}")
    print("\n💡 Next step: Run the voice agent with 'python main.py'")


if __name__ == "__main__":
    main()
