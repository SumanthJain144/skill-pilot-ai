import json
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import pandas as pd  # Added for CSV support

class DesignationVectorStore:
    def __init__(self, persist_dir="chromadb_store"):
        self.client = chromadb.PersistentClient(path=persist_dir, settings=Settings(allow_reset=True))
        self.collection = self.client.get_or_create_collection(name="designations")
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")

    def load_data(self, file_path):
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
            data = []
            for _, row in df.iterrows():
                # Collect all skill columns (Basic, Intermediate, Competent, Advanced, Expert)
                skills = [str(row.get(col, '')) for col in ["Basic", "Intermediate", "Competent", "Advanced", "Expert"] if pd.notna(row.get(col, ''))]
                data.append({
                    "designation": row["Competency Name"],
                    "skills_required": skills
                })
        else:
            with open(file_path, "r") as f:
                data = json.load(f)

        for i, entry in enumerate(data):
            text = f"Designation: {entry['designation']}\nSkills: " + "\n".join(entry["skills_required"])
            embedding = self.embedder.encode(text).tolist()

            self.collection.add(
                ids=[f"designation_{i}"],
                documents=[text],
                embeddings=[embedding],
                metadatas=[{"designation": entry["designation"]}]
            )

        print(f"✅ Loaded {len(data)} records into ChromaDB.")

    def query(self, user_input, top_k=3):
        embedding = self.embedder.encode(user_input).tolist()
        return self.collection.query(query_embeddings=[embedding], n_results=top_k)
