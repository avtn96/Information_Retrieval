import numpy as np

def create_adjacency_matrix(urls, links):
    """
    Create an adjacency matrix from the list of URLs and their links.
    """
    n = len(urls)
    adjacency_matrix = np.zeros((n, n))

    url_to_index = {url: idx for idx, url in enumerate(urls)}

    for url, out_links in links.items():
        if url in url_to_index:
            row = url_to_index[url]
            for link in out_links:
                if link in url_to_index:
                    col = url_to_index[link]
                    adjacency_matrix[row, col] = 1

    return adjacency_matrix

def calculate_page_rank(adjacency_matrix, d=0.85, max_iterations=100, tol=1e-6):
    """
    Calculate the PageRank for each page.
    """
    n = adjacency_matrix.shape[0]
    out_link_counts = adjacency_matrix.sum(axis=1)

    # Create the Google matrix
    G = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if out_link_counts[i] == 0:
                G[i, j] = 1.0 / n
            else:
                G[i, j] = adjacency_matrix[i, j] / out_link_counts[i]

    M = d * G + (1 - d) / n

    # Initialize the PageRank vector
    pr = np.ones(n) / n

    for iteration in range(max_iterations):
        new_pr = M.T @ pr
        if np.linalg.norm(new_pr - pr) < tol:
            print(f"Converged after {iteration + 1} iterations")
            break
        pr = new_pr

    return pr

if __name__ == "__main__":
    # Example URLs and their links (to be replaced with actual data)
    urls = [
        "http://example1.com",
        "http://example2.com",
        "http://example3.com",
        "http://example4.com",
        "http://example5.com",
        "http://example6.com",
        "http://example7.com",
        "http://example8.com",
        "http://example9.com",
        "http://example10.com"
    ]

    links = {
        "http://example1.com": ["http://example2.com", "http://example3.com"],
        "http://example2.com": ["http://example3.com", "http://example4.com"],
        "http://example3.com": ["http://example1.com"],
        "http://example4.com": ["http://example5.com", "http://example6.com"],
        "http://example5.com": ["http://example6.com", "http://example7.com"],
        "http://example6.com": ["http://example7.com", "http://example8.com"],
        "http://example7.com": ["http://example8.com", "http://example9.com"],
        "http://example8.com": ["http://example9.com", "http://example10.com"],
        "http://example9.com": ["http://example10.com"],
        "http://example10.com": ["http://example1.com"]
    }

    # Create the adjacency matrix
    adjacency_matrix = create_adjacency_matrix(urls, links)

    # Calculate the PageRank
    page_rank = calculate_page_rank(adjacency_matrix)

    # Display the PageRank
    for url, rank in zip(urls, page_rank):
        print(f"{url}: {rank}")
