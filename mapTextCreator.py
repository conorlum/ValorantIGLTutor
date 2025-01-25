import os

# Function to create a text file for each PNG image file in the directory and its subdirectories
def create_text_files_for_pictures(directory):
    created_files = []  # List to store paths of created text files

    # Ensure the provided directory exists
    if not os.path.isdir(directory):
        print(f"Error: The provided directory '{directory}' does not exist or is not a valid directory.")
        return
    
    # Traverse through all directories and files using os.walk()
    for root, dirs, files in os.walk(directory):
        print(f"Scanning directory: {root}")  # Debugging line to see which directories are being scanned
        
        for file in files:
            # Check if the file is a PNG image file
            if file.lower().endswith('.png'):
                # Create a path for the text file with the same name as the image file
                text_file_path = os.path.join(root, file.rsplit('.', 1)[0] + '.txt')
                
                # Check if the text file already exists
                if not os.path.isfile(text_file_path):
                    # Create and open the text file in write mode
                    with open(text_file_path, 'w') as f:
                        f.write("")  # You can write some initial content here if needed
                    
                    created_files.append(text_file_path)  # Add the created file path to the list
                    print(f"Created text file: {text_file_path}")
                else:
                    print(f"Text file already exists: {text_file_path}")

    # Print all created text files after processing
    if created_files:
        print("\nAll created text files:")
        for file in created_files:
            print(file)
    else:
        print("\nNo new text files were created.")

# Create and run the application
if __name__ == "__main__":
    print(os.getcwd())
    directory_path = "C:\\Users\\Conor Lum\\Documents\\GitHub\\ValorantIGLTutor\\mapPlans\\"  # Replace with the path of your directory
    create_text_files_for_pictures(directory_path)