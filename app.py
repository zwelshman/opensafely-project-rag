"""
OpenSAFELY Projects Semantic Search - Streamlit App
A web interface for semantically searching OpenSAFELY approved projects
"""

import streamlit as st
import json
import os
from datetime import datetime
from scraper import OpenSAFELYScraper
from semantic_search import SemanticSearchEngine, build_index_from_json


# Page config
st.set_page_config(
    page_title="OpenSAFELY Projects Search",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Initialize session state
if 'search_engine' not in st.session_state:
    st.session_state.search_engine = None
if 'projects_loaded' not in st.session_state:
    st.session_state.projects_loaded = False
if 'last_scrape' not in st.session_state:
    st.session_state.last_scrape = None


def load_search_engine():
    """Load or initialize the search engine"""
    try:
        with st.spinner("Loading search engine..."):
            engine = SemanticSearchEngine()

            # Try to load existing index
            if engine.load_index():
                st.session_state.search_engine = engine
                st.session_state.projects_loaded = True
                return True

            # Try to load from JSON
            if os.path.exists("opensafely_projects.json"):
                if engine.load_projects_from_json():
                    engine.save_index()
                    st.session_state.search_engine = engine
                    st.session_state.projects_loaded = True
                    return True

        return False
    except Exception as e:
        st.error(f"Error loading search engine: {e}")
        return False


def scrape_projects():
    """Scrape projects from OpenSAFELY website"""
    try:
        with st.spinner("Scraping OpenSAFELY projects... This may take a few minutes."):
            scraper = OpenSAFELYScraper()
            projects = scraper.scrape_all_projects(include_details=True)

            # Save to JSON
            scraper.save_projects(projects)

            # Update search engine
            engine = SemanticSearchEngine()
            engine.index_projects(projects)
            engine.save_index()

            st.session_state.search_engine = engine
            st.session_state.projects_loaded = True
            st.session_state.last_scrape = datetime.now()

            return len(projects)
    except Exception as e:
        st.error(f"Error scraping projects: {e}")
        return 0


def display_project(project, score=None):
    """Display a single project in a nice format"""
    with st.container():
        # Header with score
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"### {project.get('title', 'Untitled Project')}")
        with col2:
            if score is not None:
                st.metric("Relevance", f"{score:.1%}")

        # Metadata
        meta_cols = st.columns(3)
        if project.get('authors'):
            with meta_cols[0]:
                st.markdown(f"**Authors:** {project['authors']}")
        if project.get('status'):
            with meta_cols[1]:
                st.markdown(f"**Status:** {project['status']}")
        if project.get('date'):
            with meta_cols[2]:
                st.markdown(f"**Date:** {project['date']}")

        # Summary/Description
        if project.get('summary'):
            st.markdown(f"**Summary:** {project['summary']}")

        if project.get('full_description') and project['full_description'] != project.get('summary'):
            with st.expander("Full Description"):
                st.markdown(project['full_description'][:1000] + ("..." if len(project.get('full_description', '')) > 1000 else ""))

        # Topics
        if project.get('topics'):
            st.markdown(f"**Topics:** {project['topics']}")

        # URL
        if project.get('url'):
            st.markdown(f"[View Project Page]({project['url']})")

        st.divider()


def main():
    """Main Streamlit app"""

    # Header
    st.title("🔬 OpenSAFELY Projects Semantic Search")
    st.markdown("""
    Search through OpenSAFELY approved projects using natural language queries.
    The search uses semantic embeddings to find relevant projects based on meaning, not just keywords.
    """)

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")

        # Check if data exists
        has_data = os.path.exists("opensafely_projects.json") or os.path.exists("search_index.pkl")

        if has_data:
            st.success("✅ Project data available")
            if st.session_state.last_scrape:
                st.info(f"Last scraped: {st.session_state.last_scrape.strftime('%Y-%m-%d %H:%M')}")
        else:
            st.warning("⚠️ No project data found. Please scrape projects first.")

        st.subheader("Data Management")

        # Scrape button
        if st.button("🔄 Scrape Projects", help="Fetch latest projects from OpenSAFELY website"):
            num_projects = scrape_projects()
            if num_projects > 0:
                st.success(f"✅ Successfully scraped {num_projects} projects!")
                st.rerun()
            else:
                st.error("❌ Scraping failed. See error message above.")

        # Load button
        if has_data and not st.session_state.projects_loaded:
            if st.button("📂 Load Existing Data"):
                if load_search_engine():
                    st.success("✅ Data loaded successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to load data")

        # Stats
        if st.session_state.search_engine and st.session_state.projects_loaded:
            st.divider()
            st.subheader("📊 Statistics")
            st.metric("Total Projects", len(st.session_state.search_engine.projects))

        # Info
        st.divider()
        st.subheader("ℹ️ About")
        st.markdown("""
        This app scrapes and indexes approved projects from
        [OpenSAFELY](https://www.opensafely.org/approved-projects/)
        and enables semantic search using AI embeddings.
        """)

    # Main content
    if not st.session_state.projects_loaded:
        # Load data automatically if available
        if has_data:
            load_search_engine()

        if not st.session_state.projects_loaded:
            st.info("👈 Please load existing data or scrape projects using the sidebar.")
            return

    # Search interface
    st.header("🔍 Search Projects")

    # Search box
    query = st.text_input(
        "Enter your search query",
        placeholder="e.g., COVID-19 vaccination effectiveness, diabetes treatment outcomes, mental health during pandemic",
        help="Use natural language to describe what you're looking for"
    )

    # Number of results
    col1, col2 = st.columns([3, 1])
    with col2:
        top_k = st.slider("Results to show", min_value=1, max_value=20, value=5)

    # Search button and results
    if query:
        with st.spinner("Searching..."):
            results = st.session_state.search_engine.search(query, top_k=top_k)

        if results:
            st.success(f"Found {len(results)} relevant projects")

            # Display results
            for i, (project, score) in enumerate(results, 1):
                st.subheader(f"Result {i}")
                display_project(project, score)
        else:
            st.warning("No results found")
    else:
        # Show some example queries
        st.markdown("### 💡 Example Queries")
        examples = [
            "COVID-19 vaccine effectiveness in elderly patients",
            "Mental health outcomes during pandemic",
            "Diabetes medication adherence",
            "Cancer screening programs",
            "Cardiovascular disease risk factors"
        ]

        for example in examples:
            st.markdown(f"- {example}")

        # Show all projects option
        if st.checkbox("📋 Show all projects"):
            st.markdown("---")
            for i, project in enumerate(st.session_state.search_engine.projects, 1):
                with st.expander(f"{i}. {project.get('title', 'Untitled')}"):
                    display_project(project)


if __name__ == "__main__":
    main()
