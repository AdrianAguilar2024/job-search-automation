import os
import pandas as pd
import matplotlib.pyplot as plt
from serpapi import GoogleSearch
from pathlib import Path

# --- CONFIGURATION ---
# Define the job titles you want to search for
JOB_QUERIES = [
    "Python Developer",
    "Data Analyst",
    "Software Engineer",
    "Project Manager"
]
# Define the location for the job search
LOCATION = "United States"

def fetch_job_data(api_key, job_query, location):
    """Fetches job data for a single query using SerpApi."""
    print(f"Fetching jobs for: {job_query} in {location}...")
    params = {
        "api_key": api_key,
        "engine": "google_jobs",
        "q": f"{job_query} in {location}",
        "hl": "en",
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    
    # Check if 'jobs_results' key exists and is not empty
    if 'jobs_results' not in results or not results['jobs_results']:
        print(f"Warning: No job results found for '{job_query}'.")
        return []
        
    return results['jobs_results']

def generate_charts(df):
    """Generates and saves charts from the job data DataFrame."""
    if df.empty:
        print("DataFrame is empty. Skipping chart generation.")
        return

    print("Generating charts...")

    # Ensure the 'charts' directory exists
    Path("charts").mkdir(parents=True, exist_ok=True)

    # --- Chart 1: Number of Job Listings per Searched Role ---
    plt.figure(figsize=(10, 6))
    role_counts = df['search_query'].value_counts()
    role_counts.plot(kind='bar', color='skyblue')
    plt.title('Number of Job Postings by Role')
    plt.xlabel('Job Role')
    plt.ylabel('Number of Postings')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('charts/job_postings_by_role.png')
    plt.clf() # Clear the current figure
    print("  - Saved job_postings_by_role.png")

    # --- Chart 2: Top 15 Companies Hiring ---
    plt.figure(figsize=(10, 8))
    company_counts = df['company_name'].value_counts().nlargest(15)
    company_counts.sort_values().plot(kind='barh', color='lightgreen')
    plt.title('Top 15 Companies with Most Job Listings')
    plt.xlabel('Number of Postings')
    plt.ylabel('Company')
    plt.tight_layout()
    plt.savefig('charts/top_companies_hiring.png')
    plt.clf()
    print("  - Saved top_companies_hiring.png")

    print("Chart generation complete.")


def main():
    """Main function to run the job market analysis."""
    # For GitHub Actions, the API key is passed as an environment variable.
    api_key = os.getenv('SERPAPI_KEY')

    if not api_key:
        raise ValueError("SERPAPI_KEY environment variable not found. Please set it.")

    all_jobs = []
    for query in JOB_QUERIES:
        jobs = fetch_job_data(api_key, query, LOCATION)
        # Add the search query to each job result for later analysis
        for job in jobs:
            job['search_query'] = query
        all_jobs.extend(jobs)
    
    if not all_jobs:
        print("No jobs found across all queries. Exiting.")
        return

    # Convert the list of jobs into a pandas DataFrame for easy analysis
    df = pd.DataFrame(all_jobs)
    
    # Basic data cleaning
    df = df[['title', 'company_name', 'location', 'search_query']].dropna()

    generate_charts(df)


if __name__ == "__main__":
    main()