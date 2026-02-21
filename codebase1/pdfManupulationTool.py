import PyPDF2
import os
"""Create a PDF manipulation tool that:

Splits a PDF into individual page files

Extracts specific page ranges (e.g., pages 5-10)

Rotates pages by 90, 180, or 270 degrees

Compresses PDFs to reduce file size

Uses a menu-driven interface

Handles all operations in one script"""
def split_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page_num in range(len(reader.pages)):
            writer = PyPDF2.PdfWriter()
            writer.add_page(reader.pages[page_num])
            output_path = f"{os.path.splitext(file_path)[0]}_page_{page_num + 1}.pdf"
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            print(f"Page {page_num + 1} saved as {output_path}")
def extract_pages(file_path, start_page, end_page):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        writer = PyPDF2.PdfWriter()
        for page_num in range(start_page - 1, end_page):
            if page_num < len(reader.pages):
                writer.add_page(reader.pages[page_num])
        output_path = f"{os.path.splitext(file_path)[0]}_pages_{start_page}_to_{end_page}.pdf"
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        print(f"Pages {start_page} to {end_page} saved as {output_path}")
def rotate_pages(file_path, page_num, rotation):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        writer = PyPDF2.PdfWriter()
        for i in range(len(reader.pages)):
            page = reader.pages[i]
            if i == page_num - 1:
                page.rotate(rotation)
            writer.add_page(page)
        output_path = f"{os.path.splitext(file_path)[0]}_rotated.pdf"
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        print(f"Page {page_num} rotated by {rotation} degrees and saved as {output_path}")
def compress_pdf(file_path):
    # Note: PyPDF2 does not support compression, so this is a placeholder function.
    print("Compression is not supported by PyPDF2. Please use an external tool for compression.")
def main():
    while True:
        print("\nPDF Manipulation Tool")
        print("1. Split PDF into individual pages")
        print("2. Extract specific page ranges")
        print("3. Rotate pages")
        print("4. Compress PDF")
        print("5. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            file_path = input("Enter the PDF file path: ")
            split_pdf(file_path)
        elif choice == '2':
            file_path = input("Enter the PDF file path: ")
            start_page = int(input("Enter the start page number: "))
            end_page = int(input("Enter the end page number: "))
            extract_pages(file_path, start_page, end_page)
        elif choice == '3':
            file_path = input("Enter the PDF file path: ")
            page_num = int(input("Enter the page number to rotate: "))
            rotation = int(input("Enter rotation (90, 180, 270): "))
            rotate_pages(file_path, page_num, rotation)
        elif choice == '4':
            file_path = input("Enter the PDF file path: ")
            compress_pdf(file_path)
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")
if __name__ == "__main__":
    main()
    