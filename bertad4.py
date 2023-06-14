import requests
from bs4 import BeautifulSoup
import re

def get_css_content(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    css_links = [link["href"] for link in soup.find_all('link', href=True) if "stylesheet" in link["rel"] and 'bootstrap' not in link['href'] and 'font-awesome' not in link['href']]

    css_content = []
    for link in css_links:
        if link.startswith("/"):
            link = url + link
        elif not re.match(r'https?:\/\/', link):
            link = url + link
        css_r = requests.get(link)
        css_content.append(css_r.text)

    return css_content

def extract_css_rules(css_content):
    matched_css = {}

    for css in css_content:
        matches = re.findall(r'([^{]+)\s*{\s*([^}]+)}', css)
        for match in matches:
            selector = match[0].strip()
            properties = re.findall(r'([a-zA-Z-]+)\s*:\s*([^;]+)', match[1])
            if selector not in matched_css:
                matched_css[selector] = []
            matched_css[selector].extend(properties)

    return matched_css

def get_html_elements(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    included_tags = ['button', 'a', 'img', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'form', 'span']
    html_elements = [element for element in soup.find_all(included_tags)]

    return html_elements

url = "https://www.linkedin.com/feed/"
css_content = get_css_content(url)
css_rules = extract_css_rules(css_content)
html_elements = get_html_elements(url)

html_with_css = {}

for element in html_elements:
    element_name = element.name
    if element_name in css_rules:
        if str(element) not in html_with_css:
            html_with_css[str(element)] = []
        html_with_css[str(element)].extend(css_rules[element_name])

    # Extract inline CSS
    inline_css = element.get('style', '')
    if inline_css and str(element) in html_with_css:
        html_with_css[str(element)].append(('inline', inline_css))

output = []
for element, rules in html_with_css.items():
    css_properties = {}
    for rule in rules:
        css_properties[rule[0]] = rule[1]
    output.append({
        'HTML Element': element,
        'CSS': css_properties
    })

for item in output:
    print(item)
