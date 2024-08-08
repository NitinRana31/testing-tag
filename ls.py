import subprocess
def list_directory_contents(directory):
   try:
       # Run the `ls` command (use `dir` on Windows)
       result = subprocess.run(['ls', directory], capture_output=True, text=True, shell=True)
       if result.returncode == 0:
           print(f"Contents of {directory}:")
           print(result.stdout)
       else:
           print(f"Error listing contents of {directory}:")
           print(result.stderr)
   except Exception as e:
       print(f"Exception occurred: {e}")
if __name__ == "__main__":
   directory = "."  # You can change this to any directory you want to list
   list_directory_contents(directory)
