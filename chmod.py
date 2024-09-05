def add_chmod_command_after_wget(dockerfile_path):
   """
   Adds the 'RUN chmod +x /usr/local/tomcat10/bin/catalina.sh' command after
   the wget command and its subsequent lines in the Dockerfile.
   """
   with open(dockerfile_path, "r") as file:
       lines = file.readlines()
   # Flag to track when we've found the wget command
   wget_found = False
   # List to store modified lines
   modified_lines = []
   for i, line in enumerate(lines):
       modified_lines.append(line)
       # Check for the wget command in the current line
       if "wget --no-check-certificate https://www.artifactory.repository.net/org/apache/tomcat/tomcat/10.0.16.zip" in line:
           wget_found = True  # Set the flag to True when we find the wget line
           continue
       # If wget command was found and subsequent lines are being processed
       if wget_found:
           # Continue adding subsequent lines
           # Check if the line is the end of the block or significant (e.g., next command, empty line)
           if line.strip() == "" or line.startswith("RUN ") or line.startswith("COPY "):
               # Add the chmod command after the wget block ends
               modified_lines.append("RUN chmod +x /usr/local/tomcat10/bin/catalina.sh\n")
               wget_found = False  # Reset flag to avoid adding again
       # Move to next line
   # Write modified lines back to the Dockerfile
   with open(dockerfile_path, "w") as file:
       file.writelines(modified_lines)
   print(f"Added chmod command after the wget command block in Dockerfile at: {dockerfile_path}")
