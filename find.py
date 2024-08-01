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
   insert_content = "\n# Set up pip configuration\nWORKDIR /root/.pip\nCOPY pip.conf ./\n"
   # Insert commands after FROM in the Dockerfile
   insert_after_from(dockerfile_path, insert_content)
   print(f"Updated Dockerfile at: {dockerfile_path}")
if __name__ == "__main__":
   main()