import re
import sys
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode, unquote

# --- Python URL Tracker Remover ---
# This script reads a file, finds all URLs, and recursively removes 
# common tracking parameters from their query strings, even if they are nested.
# It includes special rules to strip parameters from specific sites and to
# standardize YouTube URLs while preserving timestamps. It then saves the 
# result to a new file.

# --- USAGE ---
#   python clean_urls.py <input_file_path>
#
#   Example:
#   python clean_urls.py a2z.json
#
#   This will create a new file named 'a2z_cleaned.json'.

# List of common tracking parameters to be removed from URLs.
TRACKING_PARAMS = {
    # Google Analytics
    'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
    # Google Ads
    'gclid',
    # Facebook
    'fbclid',
    # Microsoft Advertising
    'msclkid',
    # Mailchimp
    'mc_cid', 'mc_eid',
    # Other common trackers
    '_ga',
}

# List of sites where all query parameters and fragments should be stripped.
SITES_TO_STRIP = [
    'geeksforgeeks.org',
    'codingninjas.com',
    'leetcode.com',
]

def clean_url(url):
    """
    Recursively removes known tracking parameters from a URL.
    Includes special rules to strip all parameters and fragments from specific sites,
    and to standardize YouTube URLs, keeping only the video ID and timestamp.
    """
    try:
        # 1. Parse the URL into its components (scheme, netloc, path, etc.)
        parsed_url = urlparse(url)
        
        # --- Site-Specific Rules ---
        # Rule for sites in SITES_TO_STRIP: remove all query params and fragments.
        if any(site in parsed_url.netloc for site in SITES_TO_STRIP):
            cleaned_url_parts = parsed_url._replace(query='', fragment='')
            return urlunparse(cleaned_url_parts)
        
        # Rule for YouTube: standardize the URL, keeping only 'v' and 't' parameters.
        if 'youtube.com' in parsed_url.netloc or 'youtu.be' in parsed_url.netloc:
            video_id = None
            timestamp = None
            query_params = parse_qs(parsed_url.query)

            if 'youtube.com' in parsed_url.netloc:
                if 'v' in query_params:
                    video_id = query_params['v'][0]
            elif 'youtu.be' in parsed_url.netloc:
                video_id = parsed_url.path.lstrip('/')
            
            # Check for and preserve the timestamp parameter 't'
            if 't' in query_params:
                timestamp = query_params['t'][0]

            if video_id:
                # Build the clean URL, adding the timestamp back if it exists.
                clean_youtube_url = f"https://www.youtube.com/watch?v={video_id}"
                if timestamp:
                    clean_youtube_url += f"&t={timestamp}"
                return clean_youtube_url

        # --- General Tracker Removal ---
        # 2. Parse the query string into a dictionary of parameters.
        query_params = parse_qs(parsed_url.query)

        # 3. Recursively clean parameters
        # This new dictionary will hold parameters that are not trackers.
        cleaned_params = {}
        for key, values in query_params.items():
            # If the key is not a tracking parameter, keep it.
            if key not in TRACKING_PARAMS:
                cleaned_values = []
                for value in values:
                    # Decode the value in case it's a URL-encoded URL.
                    decoded_value = unquote(value)
                    # Check if the value itself is a URL that might have trackers.
                    if decoded_value.startswith('http://') or decoded_value.startswith('https://'):
                        # If it is, clean it recursively.
                        cleaned_values.append(clean_url(decoded_value))
                    else:
                        # Otherwise, keep the original value.
                        cleaned_values.append(value)
                cleaned_params[key] = cleaned_values

        # 4. Rebuild the query string from the cleaned dictionary
        cleaned_query = urlencode(cleaned_params, doseq=True)

        # 5. Reconstruct the URL with the cleaned query string
        cleaned_url_parts = parsed_url._replace(query=cleaned_query)
        
        return urlunparse(cleaned_url_parts)
    except Exception as e:
        # If any error occurs during parsing, return the original URL.
        print(f"⚠️  Could not parse or clean URL {url}: {e}")
        return url

def main():
    """
    Main function to execute the script logic.
    """
    # 1. Input Validation
    if len(sys.argv) < 2:
        print("Usage: python clean_urls.py <input_file_path>")
        sys.exit(1)

    input_file = sys.argv[1]

    # 2. Read the file content
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at '{input_file}'")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        sys.exit(1)

    # 3. Find all unique URLs in the content.
    # This regex is broad to catch any URL-like string inside quotes.
    urls = set(re.findall(r'https?://[^\s"]+', content))

    if not urls:
        print("No URLs found in the file.")
        return

    print(f"🔎 Found {len(urls)} unique URLs. Cleaning them now...")

    # 4. Create a mapping from original URLs to their cleaned versions.
    url_map = {}
    for url in urls:
        cleaned = clean_url(url)
        # Only add to the map if the URL was actually changed.
        if url != cleaned:
            url_map[url] = cleaned
            print(f"Original: {url}\nCleaned:  {cleaned}\n")

    # 5. Replace all tracked URLs in the original content.
    print("\n🔄 Replacing tracked URLs in the content...")
    for original, cleaned in url_map.items():
        # We replace the original URL string to ensure we don't accidentally
        # modify parts of other, longer URLs.
        content = content.replace(f'"{original}"', f'"{cleaned}"')

    # 6. Save the modified content to a new file.
    output_file = f"{input_file.split('.')[0]}_cleaned.json"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n✨ Success! Modified content saved to '{output_file}'")
    except Exception as e:
        print(f"\n❌ Error saving the file: {e}")

if __name__ == "__main__":
    main()
