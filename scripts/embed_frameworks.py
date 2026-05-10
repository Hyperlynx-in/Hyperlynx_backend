import os
import sys
from openai import OpenAI

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from application import create_app, db
from app.models import RequirementNode 

app = create_app()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_embeddings_for_requirements():
    with app.app_context():
        unembedded_nodes = RequirementNode.query.filter(RequirementNode.embedding == None).all()
        
        print(f"Found {len(unembedded_nodes)} requirements to vectorize.")
        
        batch_size = 100
        for i in range(0, len(unembedded_nodes), batch_size):
            batch = unembedded_nodes[i:i + batch_size]
            
            texts_to_embed = [
                f"{node.name or ''}. {node.description or ''}".strip()
                for node in batch
            ]
            
            try:
                response = client.embeddings.create(
                    input=texts_to_embed,
                    model="text-embedding-3-small"
                )
                
                for node, embedding_data in zip(batch, response.data):
                    node.embedding = embedding_data.embedding
                
                db.session.commit()
                print(f"Successfully vectorized batch {i//batch_size + 1}")
                
            except Exception as e:
                print(f"Error processing batch: {str(e)}")
                db.session.rollback()

if __name__ == "__main__":
    generate_embeddings_for_requirements()