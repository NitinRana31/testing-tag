import os
def find_dockerfile(base_path):
   for root, dirs, files in os.walk(base_path):
       if "Dockerfile" in files and "src" in root.split(os.sep):
           return os.path.join(root, "Dockerfile")
   return None

def insert_after_from(dockerfile_path, insert_content):
   with open(dockerfile_path, "r") as file:
       lines = file.readlines()
   new_lines = []
   from_found = False
   for line in lines:
       new_lines.append(line)
       if line.strip().lower().startswith("from") and not from_found:
           from_found = True
           new_lines.append(insert_content)
   with open(dockerfile_path, "w") as file:
       file.writelines(new_lines)

def replace_pip_install(dockerfile_path):
   # Read the Dockerfile content
   with open(dockerfile_path, "r") as file:
       lines = file.readlines()
   # Define the new pip install command
   new_pip_install = "RUN pip install --no-cache-dir -r requirements.txt\n"
   # Replace existing pip install command
   with open(dockerfile_path, "w") as file:
       for line in lines:
           if "pip install -r requirements.txt" in line:
               # Replace the line with the new command
               file.write(new_pip_install)
           else:
               file.write(line)
def main():
   # Define the base directory starting with "output"
   base_path = None
   for root, dirs, files in os.walk("."):
       if os.path.basename(root).startswith("output"):
           base_path = root
           break
   if not base_path:
       print("No directory starting with 'output' found.")
       return
   print(f"Base path found: {base_path}")
   # Find the Dockerfile path
   dockerfile_path = find_dockerfile(base_path)
   if not dockerfile_path:
       print("Dockerfile inside a 'src' folder not found.")
       return
   print(f"Dockerfile found at: {dockerfile_path}")
   # Define the content of the pip.conf file with the provided content
   pip_conf_content = "[global]\nindex-url=https://username:password@artifactrepository.citigroup.net/artifactory/api/pypi/pypi-dev/simple\n"
   pip_conf_path = os.path.join(os.path.dirname(dockerfile_path), "pip.conf")
   # Write pip.conf content to the file
   with open(pip_conf_path, "w") as f:
       f.write(pip_conf_content)
   print(f"pip.conf file has been placed at: {pip_conf_path}")
   # Content to insert after FROM command
   insert_content = (
       "\n# Set up pip configuration\n"
       "WORKDIR /root/.pip\n"
       "COPY pip.conf ./\n"
       "# Switch to root user\n"
       "USER root\n"
   )
   # Insert commands after FROM in the Dockerfile
   insert_after_from(dockerfile_path, insert_content)
   print(f"Updated Dockerfile at: {dockerfile_path}")
   # Replace existing pip install command with new one
   replace_pip_install(dockerfile_path)
   # Add the USER 1001 command to ensure non-root operation
   with open(dockerfile_path, "a") as file:
       file.write("# Set the final user\nUSER 1001\n")
   print(f"Updated Dockerfile at: {dockerfile_path}")
if __name__ == "__main__":
   main()
