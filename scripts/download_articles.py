
import json
import os
import requests
from urllib.parse import urlparse
import time
import re

def sanitize_filename(name):
    """
    Sanitizes a string to be used as a valid filename.
    """
    name = name.strip().replace(" ", "_")
    name = name.replace("[", "").replace("]", "")
    name = name.replace("(", "").replace(")", "")
    name = name.replace("/", "_")
    return re.sub(r'(?u)[^-\w.]', '', name)

def download_articles():
    """
    Downloads articles from takeuforward.org based on the links in a2z.json.
    """
    with open("a2z.json", "r") as f:
        data = json.load(f)

    for step in data:
        for sub_step in step.get("sub_steps", []):
            for topic in sub_step.get("topics", []):
                post_link = topic.get("post_link")
                if post_link:
                    try:
                        path = urlparse(post_link).path
                        # Remove trailing slash if it exists
                        if path.endswith('/'):
                            path = path[:-1]
                        
                        # Remove leading slash
                        if path.startswith('/'):
                            path = path[1:]

                        path_parts = path.split('/')
                        if len(path_parts) < 1:
                            print(f"Could not determine category for {post_link}, skipping.")
                            continue
                        
                        category = sanitize_filename(path_parts[0])
                        slug = path_parts[-1]

                        # Create directory for the category
                        dir_path = os.path.join("articles", category)
                        os.makedirs(dir_path, exist_ok=True)

                        api_url = f"https://backend.takeuforward.org/api/blog/article/{path}"
                        
                        if not slug:
                            print(f"Could not determine slug for {post_link}, skipping.")
                            continue

                        filename = os.path.join(dir_path, f"{slug}.json")

                        if os.path.exists(filename):
                            print(f"Skipping {filename}, already exists.")
                            continue

                        print(f"Downloading {api_url}")
                        response = requests.get(api_url)
                        response.raise_for_status()  # Raise an exception for bad status codes

                        with open(filename, "w") as outfile:
                            json.dump(response.json(), outfile, indent=4)
                        
                        print(f"Saved to {filename}")
                        time.sleep(1)  # Wait for 1 second between requests

                    except requests.exceptions.RequestException as e:
                        print(f"Error downloading {post_link}: {e}")
                    except Exception as e:
                        print(f"An error occurred for {post_link}: {e}")

if __name__ == "__main__":
    download_articles()
