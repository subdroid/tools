"""
Finding bibtex citations manually is sometimes (read often) a literal nightmare.
Here's a few lines of Python that takes a paper name as input and prints out the bibTex reference.

There are multiple ways in which this code cna be extended. But here's the basic version.
"""

from scholarly import scholarly

def get_bibtex_from_title(title):
    search_query = scholarly.search_pubs(title)
    paper = next(search_query, None)  # Get the first result
    if paper:
        bibtex = scholarly.bibtex(paper)
        return bibtex
    else:
        return "Paper not found"


paper_title =  input("Paper name:")
bibtex_entry = get_bibtex_from_title(paper_title)
print(bibtex_entry)
