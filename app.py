from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import urllib.robotparser

app = Flask(__name__)

def analyze_website(url):
    """
    Analyzes a website for common SEO issues.

    Args:
        url: The URL of the website to analyze.

    Returns:
        A dictionary of SEO issues and their details.
    """

    issues = {}

    try:
        # Fetch the website content
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        soup = BeautifulSoup(response.content, 'html.parser')

        # --- Check for missing or empty title tag ---
        title_tag = soup.find('title')
        if not title_tag or not title_tag.string.strip():
            issues['title_tag'] = "Missing or empty title tag"

        # --- Check for missing or empty meta description ---
        meta_description = soup.find('meta', attrs={'name': 'description'})
        if not meta_description or not meta_description.get('content', '').strip():
            issues['meta_description'] = "Missing or empty meta description"

        # --- Check for robots.txt disallow ---
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(urllib.parse.urljoin(url, '/robots.txt'))
        try:
            rp.read()
            if not rp.can_fetch("*", url):
                issues['robots_txt'] = "Robots.txt disallows crawling"
        except:
            issues['robots_txt'] = "Error accessing or parsing robots.txt"

        # --- Check for broken links ---
        # (This is a simplified check and might not be fully accurate)
        for link in soup.find_all('a'):
            href = link.get('href')
            if href and href.startswith('http'):
                try:
                    link_response = requests.head(href)  # Use HEAD request for efficiency
                    if link_response.status_code >= 400:
                        issues.setdefault('broken_links', []).append(href)
                except:
                    issues.setdefault('broken_links', []).append(href)

    except requests.exceptions.RequestException as e:
        issues['general_error'] = f"Error fetching website: {e}"

    return issues

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        seo_issues = analyze_website(url)
        return render_template('report.html', url=url, seo_issues=seo_issues)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
