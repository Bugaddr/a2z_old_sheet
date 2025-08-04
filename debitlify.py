import re
import requests
import sys
import json

# --- Python Bit.ly Link Replacer ---
# This script reads a file, finds all unique bit.ly links,
# expands them to their final destination URL, and then replaces
# them in the original content, saving the result to a new file.

# --- USAGE ---
#   python expand_and_replace.py <input_file_path>
#
#   Example:
#   python expand_and_replace.py a2z.json
#
#   This will create a new file named 'a2z_expanded.json'.

def expand_bitly_link(url):
    """
    Follows a shortened URL (like bit.ly) to its final destination.
    Uses a HEAD request for efficiency as we only need the headers.
    Includes a timeout to prevent getting stuck on slow responses.
    """
    try:
        # The `requests.head` method is faster as it doesn't download the page body.
        # `allow_redirects=True` is on by default and handles the redirection.
        # `timeout=5` prevents the script from hanging indefinitely.
        response = requests.head(url, allow_redirects=True, timeout=5)
        # The final URL is available in the 'url' attribute of the response object.
        return response.url
    except requests.RequestException as e:
        # Handle potential network errors (e.g., no connection, DNS failure).
        print(f"⚠️  Could not expand {url}: {e}")
        return url # Return the original URL if expansion fails.

def main():
    """
    Main function to execute the script logic.
    """
    # 1. Input Validation: Check if a file path is provided.
    if len(sys.argv) < 2:
        print("Usage: python expand_and_replace.py <input_file_path>")
        sys.exit(1)

    input_file = sys.argv[1]

    # 2. File Existence Check: Verify the file exists.
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at '{input_file}'")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        sys.exit(1)

    # 3. Find all unique bit.ly links using regex.
    # The pattern finds http/https links to bit.ly followed by non-quote characters.
    # Using a set automatically handles duplicates.
    bitly_links = set(re.findall(r'https?://bit\.ly/[^"]*', content))

    if not bitly_links:
        print("No bit.ly links found in the file.")
        return

    print(f"🔎 Found {len(bitly_links)} unique bit.ly links. Expanding them now...")

    # 4. Create a mapping from bit.ly links to their expanded versions.
    link_map = {}
    for link in bitly_links:
        print(f"Expanding: {link}")
        expanded = expand_bitly_link(link)
        link_map[link] = expanded
        print(f" -> {expanded}")

    # 5. Replace all occurrences in the original content.
    print("\n🔄 Replacing links in the content...")
    for original, expanded in link_map.items():
        content = content.replace(original, expanded)

    # 6. Save the modified content to a new file.
    # The output filename is derived from the input filename.
    output_file = f"{input_file.split('.')[0]}_expanded.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n✨ Success! Modified content saved to '{output_file}'")
    except Exception as e:
        print(f"\n❌ Error saving the file: {e}")


if __name__ == "__main__":
    main()
