import chromadb

# Test ChromaDB
client = chromadb.PersistentClient(path='c:/Users/d3vsh/Downloads/backupMH/chroma_insurance_db')
collection = client.get_or_create_collection(name='insurance_docs')
count = collection.count()

print(f'ChromaDB Documents: {count}')

if count > 0:
    result = collection.query(query_texts=['motor insurance'], n_results=2)
    print(f'Sample query found {len(result["documents"][0])} documents')
    print(f'First result preview: {result["documents"][0][0][:200]}...')
else:
    print('ERROR: ChromaDB is EMPTY!')
