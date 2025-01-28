import os

def edit_files(file_list_path):
    try:
        with open(file_list_path, 'r') as file_list:
            # Read the list of file paths
            files = file_list.readlines()

        # Process each file in the list
        for file_path in files:
            file_path = file_path.strip()  # Remove any extra spaces/newlines
            if os.path.exists(file_path):  # Ensure file exists
                print(f"\nOpening file: {file_path}")
                
                new_text_lines = []
                while True:
                    line = input()
                    if line == "":  # If the user presses Enter without typing, stop
                        break
                    new_text_lines.append(line)
                
                new_text = "\n".join(new_text_lines)  # Join the lines into a single string with line breaks

                # Overwrite or append the new text (based on your requirement)
                with open(file_path, 'w') as file:  # Using 'w' mode to overwrite the file
                    file.write(new_text + '\n')

                print(f"Text successfully added to {file_path}")
            else:
                print(f"File {file_path} does not exist.")

    except FileNotFoundError:
        print(f"File list '{file_list_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":

    file_list_path = 'C:\\Users\\Conor Lum\\Documents\\GitHub\\ValorantIGLTutor\\fileCreated.txt'  # Change this to your list of files
    edit_files(file_list_path)