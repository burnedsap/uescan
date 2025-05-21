import requests
from bs4 import BeautifulSoup

# Replace this with your actual Google Doc ID
DOC_ID = "1Cgj_C6d-YkrLJYBpO-zhgwfzkTFJiwFwwla0haZgPaY"
DOC_URL = f"https://docs.google.com/document/d/{DOC_ID}/export?format=html"


INDEX_PATH = "py-test.html"

def fetch_google_doc_body(doc_url):
    response = requests.get(doc_url)
    if response.status_code != 200:
        raise Exception("Failed to fetch Google Doc")
    soup = BeautifulSoup(response.text, "html.parser")
    return soup.body.decode_contents()

def update_index_html(index_path, new_body_content):
    with open(index_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Replace body content
    soup.body.clear()
    soup.body.append(BeautifulSoup(new_body_content, "html.parser"))

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(str(soup))

if __name__ == "__main__":
    print("Fetching Google Doc...")
    new_content = fetch_google_doc_body(DOC_URL)
    print("Updating index.html...")
    update_index_html(INDEX_PATH, new_content)
    print("Done.")
