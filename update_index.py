import requests
from bs4 import BeautifulSoup

# Replace this with your real Google Doc ID
DOC_ID = "1Cgj_C6d-YkrLJYBpO-zhgwfzkTFJiwFwwla0haZgPaY"
DOC_URL = f"https://docs.google.com/document/d/{DOC_ID}/export?format=html"
INDEX_HTML = "index.html"


def fetch_google_doc_body(doc_url):
    print("Fetching Google Doc...")

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(doc_url, headers=headers)

    print(f"Status Code: {response.status_code}")
    if response.status_code != 200:
        print("Response Text Preview:")
        print(response.text[:500])
        raise Exception("Failed to fetch Google Doc")

    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.body

def update_index_html(new_content):
    with open(INDEX_HTML, 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')
    old_body = soup.body
    new_body = BeautifulSoup(str(new_content), 'html.parser').body

    old_body.clear()
    for tag in new_body.contents:
        old_body.append(tag)

    with open(INDEX_HTML, 'w', encoding='utf-8') as f:
        f.write(str(soup.prettify()))

    print("✅ index.html updated.")

if __name__ == "__main__":
    try:
        new_content = fetch_google_doc_body(DOC_URL)
        update_index_html(new_content)
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)
