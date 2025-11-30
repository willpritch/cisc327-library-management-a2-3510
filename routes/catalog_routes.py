"""
Catalog Routes - Book catalog related endpoints
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import get_all_books
from services.library_service import add_book_to_catalog

catalog_bp = Blueprint('catalog', __name__)

@catalog_bp.route('/')
def index():
    """Home page redirects to catalog."""
    return redirect(url_for('catalog.catalog'))

@catalog_bp.route('/catalog')
def catalog():
    """
    Display all books in the catalog.
    Implements R2: Book Catalog Display
    """
    books = get_all_books()
    return render_template('catalog.html', books=books)


@catalog_bp.route("/add_book", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        isbn = request.form.get("isbn", "").strip()
        total_copies_raw = request.form.get("total_copies", "").strip()

        try:
            total_copies = int(total_copies_raw)
        except ValueError:
            flash("Total copies must be a positive integer.", "error")
            return render_template("add_book.html")

        success, message = add_book_to_catalog(title, author, isbn, total_copies)

        if success:
            flash(message, "success")
            return redirect(url_for("catalog.catalog"))
        else:
            flash(message, "error")
            return render_template("add_book.html")

    return render_template("add_book.html")