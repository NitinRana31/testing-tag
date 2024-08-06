import os

def find_dockerfiles(base_path):
    dockerfiles = []
    for root, dirs, files in os.walk(base_path):
        if "src" in root:
            for file in files:
                if file == "Dockerfile":
                    dockerfiles.append(os.path.join(root, file))
    return dockerfiles

def determine_application_type(dockerfile_path):
    with open(dockerfile_path, "r") as file:
        content = file.read()
        if "pip install" in content or "python" in content:
            return "python"
        elif "mvn" in content or "java" in content:
            return "java"
    return "unknown"

def remove_mvnw_files(dockerfile_directory):
    mvnw_path = os.path.join(dockerfile_directory, "mvnw")
    mvnw_cmd_path = os.path.join(dockerfile_directory, "mvnw.cmd")

    if os.path.exists(mvnw_path):
        os.remove(mvnw_path)
        print(f"Removed {mvnw_path}")
    else:
        print(f"No mvnw file found at {mvnw_path}")

    if os.path.exists(mvnw_cmd_path):
        os.remove(mvnw_cmd_path)
        print(f"Removed {mvnw_cmd_path}")
    else:
        print(f"No mvnw.cmd file found at {mvnw_cmd_path}")

def process_dockerfile(dockerfile_path):
    dockerfile_directory = os.path.dirname(dockerfile_path)
    app_type = determine_application_type(dockerfile_path)
    print(f"Application type determined: {app_type} for Dockerfile at {dockerfile_path}")

    if app_type == "java":
        remove_mvnw_files(dockerfile_directory)
    else:
        print(f"Skipping non-Java Dockerfile at {dockerfile_path}")

def main():
    base_path = None
    for root, dirs, files in os.walk("."):
        if os.path.basename(root).startswith("output"):
            base_path = root
            break

    if not base_path:
        print("No directory starting with 'output' found.")
        return

    print(f"Base path found: {base_path}")
    dockerfiles = find_dockerfiles(base_path)

    if not dockerfiles:
        print("No Dockerfiles inside 'src' folders found.")
        return

    for dockerfile_path in dockerfiles:
        print(f"Dockerfile found at: {dockerfile_path}")
        process_dockerfile(dockerfile_path)

if __name__ == "__main__":
    main()
