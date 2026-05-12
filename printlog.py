import os
import glob

import nlpertools


def get_latest_file(directory):
    """Find the latest file in the given directory."""
    files = glob.glob(os.path.join(directory, "*"))
    if not files:
        return None
    latest_file = max(files, key=os.path.getmtime)
    return latest_file


# Example usage:
if __name__ == "__main__":
    latest_file_path = get_latest_file(r"C:\Users\23702\Desktop\CoreCoder\logs")
    print("Latest file:", latest_file_path)
    data = nlpertools.load_json(latest_file_path)
    print(data["input"][0]["content"])
