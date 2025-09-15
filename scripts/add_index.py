import json
import os
import argparse
from bs4 import BeautifulSoup

def get_slug(path):
    if not path:
        return None
    # Get the last part of the path
    slug = os.path.basename(path.strip('/'))
    # Remove extension if it exists
    slug = os.path.splitext(slug)[0]
    return slug

def add_indices_to_json(html_content, json_filepath):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Create a map from slug to index
    slug_to_index = {}
    for i, a in enumerate(soup.find_all('a')):
        href = a.get('href')
        slug = get_slug(href)
        if slug:
            slug_to_index[slug] = i

    with open(json_filepath, 'r') as f:
        data = json.load(f)

    for step in data:
        for sub_step in step.get('sub_steps', []):
            for topic in sub_step.get('topics', []):
                post_link = topic.get('post_link')
                if post_link:
                    slug = get_slug(post_link)
                    if slug and slug in slug_to_index:
                        topic['index'] = slug_to_index[slug]

    with open(json_filepath, 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Add an index to articles in a JSON file based on an HTML file.")
    parser.add_argument("html_filepath", help="Path to the HTML file containing the article order.")
    parser.add_argument("json_filepath", help="Path to the JSON file to be updated.")
    args = parser.parse_args()

    with open(args.html_filepath, 'r') as f:
        html_content = f.read()

    add_indices_to_json(html_content, args.json_filepath)
