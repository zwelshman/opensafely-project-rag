"""
Semantic Search Engine for OpenSAFELY Projects
Uses sentence transformers to create embeddings and enable semantic search
"""

import json
import numpy as np
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
import pickle
import os


class SemanticSearchEngine:
    """Semantic search engine using sentence transformers"""

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the semantic search engine

        Args:
            model_name: Name of the sentence transformer model to use
                       'all-MiniLM-L6-v2' is a good balance of speed and quality
        """
        print(f"Loading model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.projects = []
        self.embeddings = None
        self.index_path = "search_index.pkl"

    def prepare_project_text(self, project: Dict[str, str]) -> str:
        """
        Prepare searchable text from a project dictionary

        Args:
            project: Project dictionary with various fields

        Returns:
            Combined text string for embedding
        """
        # Combine relevant fields for search
        text_parts = []

        if project.get('title'):
            text_parts.append(f"Title: {project['title']}")

        if project.get('summary'):
            text_parts.append(f"Summary: {project['summary']}")

        if project.get('full_description'):
            text_parts.append(f"Description: {project['full_description']}")
        elif project.get('description'):
            text_parts.append(f"Description: {project['description']}")

        if project.get('authors'):
            text_parts.append(f"Authors: {project['authors']}")

        if project.get('topics'):
            text_parts.append(f"Topics: {project['topics']}")

        if project.get('status'):
            text_parts.append(f"Status: {project['status']}")

        return " ".join(text_parts)

    def index_projects(self, projects: List[Dict[str, str]]) -> None:
        """
        Index projects by creating embeddings

        Args:
            projects: List of project dictionaries
        """
        print(f"Indexing {len(projects)} projects...")
        self.projects = projects

        # Prepare texts for embedding
        texts = [self.prepare_project_text(project) for project in projects]

        # Create embeddings
        print("Creating embeddings...")
        self.embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=True
        )

        print(f"Created embeddings with shape: {self.embeddings.shape}")

    def save_index(self, filepath: str = None) -> None:
        """Save the search index to disk"""
        filepath = filepath or self.index_path
        index_data = {
            'projects': self.projects,
            'embeddings': self.embeddings
        }
        with open(filepath, 'wb') as f:
            pickle.dump(index_data, f)
        print(f"Index saved to {filepath}")

    def load_index(self, filepath: str = None) -> bool:
        """
        Load a previously saved search index

        Returns:
            True if successful, False otherwise
        """
        filepath = filepath or self.index_path
        if not os.path.exists(filepath):
            return False

        try:
            with open(filepath, 'rb') as f:
                index_data = pickle.load(f)
            self.projects = index_data['projects']
            self.embeddings = index_data['embeddings']
            print(f"Loaded index with {len(self.projects)} projects")
            return True
        except Exception as e:
            print(f"Error loading index: {e}")
            return False

    def search(self, query: str, top_k: int = 5) -> List[Tuple[Dict[str, str], float]]:
        """
        Search for projects using semantic similarity

        Args:
            query: Search query string
            top_k: Number of top results to return

        Returns:
            List of (project, score) tuples, sorted by relevance
        """
        if self.embeddings is None or len(self.projects) == 0:
            print("No projects indexed. Please index projects first.")
            return []

        # Encode the query
        query_embedding = self.model.encode([query], convert_to_numpy=True)[0]

        # Calculate cosine similarity
        similarities = np.dot(self.embeddings, query_embedding) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
        )

        # Get top k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]

        # Return results with scores
        results = [
            (self.projects[idx], float(similarities[idx]))
            for idx in top_indices
        ]

        return results

    def load_projects_from_json(self, filepath: str = "opensafely_projects.json") -> bool:
        """
        Load and index projects from a JSON file

        Args:
            filepath: Path to the JSON file containing projects

        Returns:
            True if successful, False otherwise
        """
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            return False

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                projects = json.load(f)

            if not projects:
                print("No projects found in file")
                return False

            self.index_projects(projects)
            return True
        except Exception as e:
            print(f"Error loading projects: {e}")
            return False


def build_index_from_json(
    json_file: str = "opensafely_projects.json",
    index_file: str = "search_index.pkl",
    model_name: str = 'all-MiniLM-L6-v2'
) -> SemanticSearchEngine:
    """
    Build a search index from a JSON file of projects

    Args:
        json_file: Path to JSON file with scraped projects
        index_file: Path to save the search index
        model_name: Sentence transformer model to use

    Returns:
        Initialized SemanticSearchEngine
    """
    engine = SemanticSearchEngine(model_name=model_name)

    # Try to load existing index
    if engine.load_index(index_file):
        print("Loaded existing index")
        return engine

    # Build new index
    if engine.load_projects_from_json(json_file):
        engine.save_index(index_file)
        return engine
    else:
        raise Exception(f"Failed to load projects from {json_file}")


def main():
    """Demo of the semantic search engine"""
    # Build or load index
    engine = build_index_from_json()

    # Interactive search
    print("\n" + "="*50)
    print("OpenSAFELY Projects Semantic Search")
    print("="*50)

    while True:
        query = input("\nEnter search query (or 'quit' to exit): ").strip()
        if query.lower() in ['quit', 'exit', 'q']:
            break

        if not query:
            continue

        results = engine.search(query, top_k=5)

        print(f"\nTop {len(results)} results for '{query}':\n")
        for i, (project, score) in enumerate(results, 1):
            print(f"{i}. [{score:.3f}] {project.get('title', 'No title')}")
            if project.get('summary'):
                print(f"   {project['summary'][:150]}...")
            if project.get('url'):
                print(f"   URL: {project['url']}")
            print()


if __name__ == "__main__":
    main()
