
import os


DOWNLOADS_DIR = "/mnt/c/Users/mubar/Downloads"
def search_downloads(keyword: str) -> list[str]:
    print(f"[DEBUG] DOWNLOADS_DIR = {DOWNLOADS_DIR}")
    print(f"[DEBUG] exists? {os.path.isdir(DOWNLOADS_DIR)}")
    print(f"[DEBUG] searching for keyword = {keyword!r}")

    keyword_lower = keyword.lower()
    matches = []
    total_files_seen = 0

    for root, _, files in os.walk(DOWNLOADS_DIR):
        for filename in files:
            total_files_seen += 1
            if keyword_lower in filename.lower():
                matches.append(os.path.join(root, filename))

    print(f"[DEBUG] total files scanned: {total_files_seen}, matches: {len(matches)}")
    return matches[:50]

if __name__ == "__main__":
    # Test the search_downloads function with a sample keyword
    test_keyword = "CV"
    results = search_downloads(test_keyword)
    print(f"Search results for '{test_keyword}':")
    for result in results:
        print(result)