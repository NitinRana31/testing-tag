import os
def find_base_path():
   """
   Finds the base path that starts with 'output' from the current directory.
   """
   for root, dirs, files in os.walk("."):
       if os.path.basename(root).startswith("output"):
           return root
   print("No directory starting with 'output' found.")
   return None
def find_dockerfiles_with_target(base_path):
   """
   Finds all Dockerfiles under the base path and checks if a 'target' directory exists beside each Dockerfile.
   """
   dockerfiles_with_target = []
   for root, dirs, files in os.walk(base_path):
       if 'Dockerfile' in files and 'target' in dirs:
           dockerfile_path = os.path.join(root, 'Dockerfile')
           dockerfiles_with_target.append(dockerfile_path)
   return dockerfiles_with_target
def find_jar_in_target(dockerfile_directory):
   """
   Finds the first .jar file in the 'target' directory beside the Dockerfile.
   """
   target_dir = os.path.join(dockerfile_directory, "target")
   if os.path.exists(target_dir):
       for file in os.listdir(target_dir):
           if file.endswith(".jar"):
               return file
   return None
def replace_jar_placeholder_in_dockerfile(dockerfile_path, jar_file):
   """
   Replaces the placeholder '${project.artifactId}-${project.version}.jar' in the 'COPY' command
   with the actual jar file found in the 'target' directory.
   """
   with open(dockerfile_path, "r") as file:
       lines = file.readlines()
   with open(dockerfile_path, "w") as file:
       for line in lines:
           # Replace only the placeholder part, not the entire 'COPY' command
           if "COPY target/${project.artifactId}-${project.version}.jar" in line:
               line = line.replace("${project.artifactId}-${project.version}.jar", jar_file)
           file.write(line)
   print(f"Replaced .jar placeholder with '{jar_file}' in Dockerfile at: {dockerfile_path}")
def process_dockerfiles(base_path):
   """
   Processes each Dockerfile found to replace the .jar placeholder with the actual .jar file.
   """
   dockerfiles = find_dockerfiles_with_target(base_path)
   if not dockerfiles:
       print("No Dockerfiles with associated 'target' directories found.")
       return
   for dockerfile_path in dockerfiles:
       dockerfile_directory = os.path.dirname(dockerfile_path)
       jar_file = find_jar_in_target(dockerfile_directory)
       if jar_file:
           replace_jar_placeholder_in_dockerfile(dockerfile_path, jar_file)
       else:
           print(f"No .jar file found in the 'target' directory beside Dockerfile at: {dockerfile_path}")
def main():
   base_path = find_base_path()  # Use the base path detection logic from the previous script
   if not base_path:
       return  # Exit if no base path is found
   print(f"Base path found: {base_path}")
   process_dockerfiles(base_path)
if __name__ == "__main__":
   main()
