"""Create a Book Catalog API that:

Reads book data from a text file (CSV

Use this CSV file as data source.

Implements RESTful API endpoints for CRUD operations:

GET /books - List all books

GET /books/{id} - Get a specific book by ID

POST /books - Add a new book

PUT /books/{id} - Update a book

DELETE /books/{id} - Delete a book

Returns data in JSON format

Handles common HTTP status codes (200, 201, 404, 400)

Persists changes back to the text file

Includes search and filter functionality

Bonus (optional):"""
# Implement pagination for the GET /books endpoint
# Add user authentication for modifying data (POST, PUT, DELETE)
import csv
from flask import Flask, jsonify, request, abort
app = Flask(__name__)
BOOKS_FILE = r'C:\Users\206136\OneDrive - Cognizant\Desktop\Python\DailyProjects\SourceFiles\books.csv'
def read_books():
    """Read books from the CSV file."""
    books = []
    try:
        with open(BOOKS_FILE, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                books.append(row)
    except FileNotFoundError:
        pass  # If the file doesn't exist, return an empty list
    return books
def write_books(books):
    """Write books to the CSV file."""
    with open(BOOKS_FILE, mode='w', newline='') as file:
        fieldnames = ['id', 'title', 'author', 'year']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for book in books:
            writer.writerow(book)
@app.route('/books', methods=['GET'])
def get_books():
    """Get a list of all books."""
    books = read_books()
    return jsonify(books), 200
@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """Get a specific book by ID."""
    books = read_books()
    book = next((b for b in books if int(b['id']) == book_id), None)
    if book is None:
        abort(404, description="Book not found")
    return jsonify(book), 200
@app.route('/books', methods=['POST'])
def add_book():
    """Add a new book."""
    if not request.json or not 'title' in request.json:
        abort(400, description="Title is required")
    books = read_books()
    new_id = max([int(b['id']) for b in books], default=0) + 1
    new_book = {
        'id': str(new_id),
        'title': request.json['title'],
        'author': request.json.get('author', ''),
        'year': request.json.get('year', '')
    }
    books.append(new_book)
    write_books(books)
    return jsonify(new_book), 201
@app.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    """Update a book."""
    if not request.json:
        abort(400, description="Request body must be JSON")
    books = read_books()
    book = next((b for b in books if int(b['id']) == book_id), None)
    if book is None:
        abort(404, description="Book not found")
    book['title'] = request.json.get('title', book['title'])
    book['author'] = request.json.get('author', book['author'])
    book['year'] = request.json.get('year', book['year'])
    write_books(books)
    return jsonify(book), 200
@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    """Delete a book."""
    books = read_books()
    book = next((b for b in books if int(b['id']) == book_id), None)
    if book is None:
        abort(404, description="Book not found")
    books.remove(book)
    write_books(books)
    return jsonify({'result': True}), 200
if __name__ == '__main__':
    app.run(debug=True)
