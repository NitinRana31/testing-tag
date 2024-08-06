import os

def find_and_remove_mvnw_files(base_path):
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file in ["mvnw", "mvnw.cmd"]:
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f"Removed {file_path}")

def main():
    # Assuming the script is placed beside the 'src' directory
    base_path = os.path.join(os.path.dirname(__file__), "src")

    if not os.path.exists(base_path):
        print(f"No 'src' directory found beside the script.")
        return

    print(f"Searching for mvnw and mvnw.cmd files in {base_path}...")
    find_and_remove_mvnw_files(base_path)

if __name__ == "__main__":
    main()
