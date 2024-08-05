import os
import stat
def find_dockerfile(base_path):
   for root, dirs, files in os.walk(base_path):
       if "src" in root:
           for file in files:
               if file == "Dockerfile":
                   return os.path.join(root, file)
   return None
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
   dockerfile_path = find_dockerfile(base_path)
   if not dockerfile_path:
       print("Dockerfile inside a 'src' folder not found.")
       return
   print(f"Dockerfile found at: {dockerfile_path}")
   dockerfile_directory = os.path.dirname(dockerfile_path)
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
   make_mvnw_executable(dockerfile_directory)
if __name__ == "__main__":
   main()
