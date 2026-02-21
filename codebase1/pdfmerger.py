"""
THE APP:
PDF merger that scans a folder for all PDF files and combines them into one.
User specifies folder path or uses current directory.

WHAT TO FIGURE OUT:
- How do you list all files in a folder?
- How do you filter for PDF files only?
- How do you check if a folder exists?
- How do you merge PDFs in alphabetical order?
- How do you handle file paths correctly?

START HERE:
First, ask for folder path (or use current directory).
Then scan the folder for all .pdf files.
Finally, merge them in alphabetical order.

KEY CONCEPT:
Use os.listdir() to get all files in a folder.
Use .endswith('.pdf') to filter PDF files.
Use os.path.join() to create full file paths.
Use .sort() to arrange files alphabetically.
Empty string from input() means use current directory.
"""

#---------------------------------------------
# THE CODE SKELETON

# Import necessary libraries
# (PyPDF2 for PDF operations, os for file handling)
import PyPDF2
import os


# Print header
print("PDF Merger - Combine all PDFs in a folder into one file")


# Ask for folder path
# (empty input means current directory)
folder_path = input("Enter folder path (leave empty for current directory): ").strip()

# Use current directory if input is empty
if not folder_path:
    folder_path = os.getcwd()

# Check if folder exists
if not os.path.isdir(folder_path):
    print(f"Error: Folder '{folder_path}' does not exist.")
    exit(1)

# Find all PDF files in the folder
# (scan directory and filter for .pdf files)
pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]

# Sort files alphabetically
pdf_files.sort()

# Check if any PDFs were found
if not pdf_files:
    print(f"No PDF files found in '{folder_path}'.")
    exit(1)
# Display found PDF files
print(f"Found {len(pdf_files)} PDF files:")

# Get output filename from user
output_filename = input("Enter output filename (without .pdf extension): ").strip()

# Add .pdf extension if missing
if not output_filename.lower().endswith('.pdf'):
    output_filename += '.pdf'

# Print merging status
print(f"Merging {len(pdf_files)} PDF files into '{output_filename}'...")

# Create merger object and page counter
merger = PyPDF2.PdfMerger()
total_pages = 0

# Loop through each PDF file
for pdf_file in pdf_files:
    # Append PDF to merger
    pdf_path = os.path.join(folder_path, pdf_file)
    merger.append(pdf_path)   
    # Count pages
    with open(pdf_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        num_pages = len(reader.pages)
        total_pages += num_pages
  
    # Print progress
    print(f"Added '{pdf_file}' ({num_pages} pages)")
    
# Save merged PDF
print(f"Saving merged PDF as '{output_filename}' with {total_pages} total pages...")
merger.write(output_filename)

# Close merger
merger.close()

# Print completion summary
print(f"Merge complete! '{output_filename}' created with {total_pages} pages.")