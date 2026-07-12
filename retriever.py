from langchain_mistralai import MistralAIEmbeddings
from supabase import create_client
import config


def hybrid_retrieve(query, k=5, filename=None):
    """Vector search via Supabase. If filename is given, results are scoped
    to chunks whose metadata.source matches it exactly."""
    embeddings = MistralAIEmbeddings(model="mistral-embed", api_key=config.MISTRAL_API_KEY)
    supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)

    query_vector = embeddings.embed_query(query)

    response = supabase.rpc("match_documents", {
        "query_embedding": query_vector,
        "match_count": k,
        "filter_source": filename
    }).execute()

    return response.data


if __name__ == "__main__":
    results = hybrid_retrieve("your test question here", k=3)
    for r in results:
        print(r["metadata"], "-", r["content"][:100], "...\n")