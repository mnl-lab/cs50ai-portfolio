import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(link for link in pages[filename] if link in pages)

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    c = (1 - damping_factor) / len(
        corpus
    )  # the constant representing the  probability of the event that a random link is chosen from all pages
    result = {
        i: c for i in corpus.keys()
    }  # it is present in all pages so we initialise the result with it
    if not len(corpus[page]):  # is a page has no links then that's the result
        return result
    for i in corpus[page]:  # if the page has links we iterate over the linked pages
        # for every neighboring page we add "damping_factor/ len(corpus[page])" representing that this page is chosen
        result[i] += damping_factor / len(corpus[page])
    return result


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    page = random.choice(list(corpus.keys()))  # the first page is chosen at random
    result = {i: 0 for i in corpus.keys()}
    for i in range(n):
        result[page] += 1  # meaning that the page has been visited
        distribution = transition_model(
            corpus, page, damping_factor
        )  # we calculat the distribution of the random variable representinf next_paage
        pages = list(distribution.keys())
        probas = list(distribution.values())
        page = random.choices(pages, weights=probas, k=1)[
            0
        ]  # randomly choose a page from there using the probability as weights
    # normalisation:
    for i in result:
        result[i] /= n  # divide everything on n
    return result


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    N = len(corpus)
    result_p = {i: 1 / len(corpus) for i in corpus.keys()}  # the PR we start with
    result_n = {i: 0 for i in corpus.keys()}
    it = 1  # iterator for the while loop
    while it:  # a while loop to mark a stop
        for i in corpus:
            somme = 0  # initialisin the sum in the formula
            # sum calculation followinng the rules
            for page in corpus:
                if corpus[page]:
                    if i in corpus[page]:
                        somme += result_p[page] / len(corpus[page])
                else:
                    somme += result_p[page] / N
            # gathering the formula
            result_n[i] = ((1 - damping_factor) / N) + damping_factor * somme

        if all(
            abs(result_p[i] - result_n[i]) < 0.001 for i in corpus
        ):  # the condition that there no value between result_p and result_n changed by more that 0.001
            it = 0  # this iteration should be the last one
        # change the previous to the current and reinitialise the current
        result_p = result_n.copy()
        result_n = {i: 0 for i in corpus.keys()}

    return result_p  # returning the result


if __name__ == "__main__":
    main()
