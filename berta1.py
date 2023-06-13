import requests
from bs4 import BeautifulSoup
import json
from sentence_transformers import SentenceTransformer, util
import numpy as np

def json_to_sentence(json_object):
    parts = []
    for key, value in json_object.items():
        parts.append(f"{key} is {value}")
    return ", ".join(parts)

def parse_node(node):
    tag_dict = {"tag": node.name}
    
    # add attributes to the dictionary
    for attr, val in node.attrs.items():
        tag_dict[attr] = val
        
    # add text if the node is not self-closing and actually contains text
    if node.string:
        tag_dict["text"] = node.string.strip()

    return tag_dict

# URL of the webpage you want to access
url = "https://en.wikipedia.org/wiki/Main_Page"

# Send HTTP request to the specified URL and save the response from server in a response object called r
r = requests.get(url)

# Create a BeautifulSoup object and specify the parser
soup = BeautifulSoup(r.text, 'html.parser')

# Define the tags you're interested in
tags = ['button', 'a', 'img', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'form', 'span']


html_dicts = [parse_node(node) for node in soup.recursiveChildGenerator() if node.name and node.name in tags]


htmls_sentences = [json_to_sentence(html) for html in html_dicts]


english = 'Diodorus scytobrachion '
sentences = [english] + htmls_sentences

model = SentenceTransformer('all-MiniLM-L12-v2')


embeddings = model.encode(sentences, convert_to_tensor=True)


cosine_scores = util.pytorch_cos_sim(embeddings, embeddings)

cosine_scores_np = cosine_scores.numpy()

print(f"Sentence: {sentences[0]}")

max_score = -np.inf
max_index = None

for j, score in enumerate(cosine_scores_np[0]):

    if j != 0 and score > max_score:
        max_score = score
        max_index = j

htmls_json = [json.dumps(html) for html in html_dicts]


for html_json in htmls_json:
    print(html_json)        

print(f"\tHighest similarity is with '{sentences[max_index]}': {max_score}")
