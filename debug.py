import os
import shutil
import stat
import subprocess

def find_dockerfiles(base_path):
    dockerfiles = []
    for root, dirs, files in os.walk(base_path):
        if 'output' in root.split(os.sep) and 'source' in root.split(os.sep):
            for file in files:
                if file == "Dockerfile":
                    dockerfiles.append(os.path.join(root, file))
    return dockerfiles

def find_pom_directories(base_path):
    pom_directories = []
    for root, dirs, files in os.walk(base_path):
        if 'pom.xml' in files:
            pom_directories.append(root)
    return pom_directories

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
        make_mvnw_executable(dockerfile_directory)
    else:
        print("Unknown application type. No changes made.")

def copy_settings_xml_to_pom_directories(base_path):
    settings_xml_source = os.path.join(os.path.dirname(base_path), "settings.xml")
    if not os.path.exists(settings_xml_source):
        print(f"settings.xml not found at {settings_xml_source}")
        return
    
    pom_directories = find_pom_directories(base_path)
    
    for pom_directory in pom_directories:
        settings_xml_destination = os.path.join(pom_directory, "settings.xml")
        shutil.copy(settings_xml_source, settings_xml_destination)
        print(f"Copied settings.xml to {settings_xml_destination}")
        
        # Run the mvn clean package -s settings.xml command
        try:
            print(f"Running mvn clean package in {pom_directory}")
            
            command = [
                "mvn", "clean", "package",
                "-Dmaven.wagon.http.ssl.insecure=true",
                "-Dmaven.wagon.http.ssl.allowall=true"
            ]
            
            result = subprocess.run(command, cwd=pom_directory, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Successfully ran mvn clean package in {pom_directory}")
            else:
                print(f"Failed to run mvn clean package in {pom_directory}. Error: {result.stderr}")
                print(f"Command output: {result.stdout}")
        except Exception as e:
            print(f"Exception occurred while running mvn clean package in {pom_directory}: {e}")
            print(f"Exception details: {str(e)}")
            
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
    copy_settings_xml_to_pom_directories(base_path)

if __name__ == "__main__":
    main()
