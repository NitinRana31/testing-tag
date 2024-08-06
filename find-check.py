import os
import shutil
import stat

def find_dockerfiles(base_path):
    dockerfiles = []
    for root, dirs, files in os.walk(base_path):
        if "src" in root:
            for file in files:
                if file == "Dockerfile":
                    dockerfiles.append(os.path.join(root, file))
    return dockerfiles

def insert_after_from(dockerfile_path, insert_content):
    with open(dockerfile_path, "r") as file:
        lines = file.readlines()
    with open(dockerfile_path, "w") as file:
        for line in lines:
            file.write(line)
            if line.startswith("FROM"):
                file.write(insert_content)

def replace_pip_install(dockerfile_path):
    with open(dockerfile_path, "r") as file:
        lines = file.readlines()
    new_pip_install = "RUN pip install --no-cache-dir -r requirements.txt\n"
    with open(dockerfile_path, "w") as file:
        for line in lines:
            if "pip install -r requirements.txt" in line:
                file.write(new_pip_install)
            else:
                file.write(line)

def make_mvnw_executable(dockerfile_directory):
    mvnw_path = os.path.join(dockerfile_directory, "mvnw")
    if os.path.exists(mvnw_path):
        st = os.stat(mvnw_path)
        os.chmod(mvnw_path, st.st_mode | stat.S_IEXEC)
        print(f"Made {mvnw_path} executable.")
    else:
        print(f"No mvnw file found at {mvnw_path}.")

def determine_application_type(dockerfile_path):
    with open(dockerfile_path, "r") as file:
        content = file.read()
        if "pip install" in content or "python" in content:
            return "python"
        elif "mvn" in content or "java" in content:
            return "java"
    return "unknown"

def modify_java_dockerfile(dockerfile_path):
    dockerfile_directory = os.path.dirname(dockerfile_path)
    settings_xml_source = os.path.join(os.path.dirname(base_path), "settings.xml")
    settings_xml_destination = os.path.join(dockerfile_directory, "settings.xml")

    # Copy settings.xml to the same directory as the Dockerfile
    if os.path.exists(settings_xml_source):
        shutil.copy(settings_xml_source, settings_xml_destination)
        print(f"Copied settings.xml to {settings_xml_destination}")
    else:
        print(f"settings.xml not found at {settings_xml_source}")

    with open(dockerfile_path, "r") as file:
        lines = file.readlines()
    
    with open(dockerfile_path, "w") as file:
        inserted = False
        for line in lines:
            if line.startswith("COPY mvnw ."):
                continue  # Remove this line
            if line.startswith("RUN ./mvnw dependency:go-offline"):
                continue  # Remove this line
            if line.startswith("RUN ./mvnw clean package"):
                if "-s settings.xml" not in line:
                    line = line.replace("./mvnw clean package", "mvn clean package -s settings.xml")
            file.write(line)
            if not inserted and line.startswith("WORKDIR"):
                file.write("COPY settings.xml .\n")
                inserted = True

def process_dockerfile(dockerfile_path):
    dockerfile_directory = os.path.dirname(dockerfile_path)
    app_type = determine_application_type(dockerfile_path)
    print(f"Application type determined: {app_type} for Dockerfile at {dockerfile_path}")

    if app_type == "python":
        pip_conf_content = "[global]\nindex-url=https://username:password@artifactrepository.citigroup.net/artifactory/api/pypi/pypi-dev/simple\n"
        pip_conf_path = os.path.join(dockerfile_directory, "pip.conf")
        with open(pip_conf_path, "w") as f:
            f.write(pip_conf_content)
        print(f"pip.conf file has been placed at: {pip_conf_path}")

        insert_content = (
            "\n# Set up pip configuration\n"
            "WORKDIR /root/.pip\n"
            "COPY pip.conf ./\n"
            "# Switch to root user\n"
            "USER root\n"
        )
        insert_after_from(dockerfile_path, insert_content)
        print(f"Updated Dockerfile at: {dockerfile_path}")

        replace_pip_install(dockerfile_path)
        with open(dockerfile_path, "a") as file:
            file.write("# Set the final user\nUSER 1001\n")
        print(f"Updated Dockerfile at: {dockerfile_path}")

    elif app_type == "java":
        modify_java_dockerfile(dockerfile_path)
        make_mvnw_executable(dockerfile_directory)

    else:
        print("Unknown application type. No changes made.")

def main():
    global base_path
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
