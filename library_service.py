"""
Library Service Module - Business Logic Functions
Contains all the core business logic for the Library Management System
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from database import (
    get_book_by_id, get_book_by_isbn, get_patron_borrow_count,
    insert_book, insert_borrow_record, update_book_availability,
    update_borrow_record_return_date, get_all_books
)
import re

def add_book_to_catalog(title: str, author: str, isbn: str, total_copies: int) -> Tuple[bool, str]:
    """
    Add a new book to the catalog.
    Implements R1: Book Catalog Management
    
    Args:
        title: Book title (max 200 chars)
        author: Book author (max 100 chars)
        isbn: 13-digit ISBN
        total_copies: Number of copies (positive integer)
        
    Returns:
        tuple: (success: bool, message: str)
    """
    # Input validation
    if not title or not title.strip():
        return False, "Title is required."
    
    if len(title.strip()) > 200:
        return False, "Title must be less than 200 characters."
    
    if not author or not author.strip():
        return False, "Author is required."
    
    if len(author.strip()) > 100:
        return False, "Author must be less than 100 characters."
    
    if len(isbn) != 13:
        return False, "ISBN must be exactly 13 digits."
    
    if not isinstance(total_copies, int) or total_copies <= 0:
        return False, "Total copies must be a positive integer."
    
    # Check for duplicate ISBN
    existing = get_book_by_isbn(isbn)
    if existing:
        return False, "A book with this ISBN already exists."
    
    # Insert new book
    success = insert_book(title.strip(), author.strip(), isbn, total_copies, total_copies)
    if success:
        return True, f'Book "{title.strip()}" has been successfully added to the catalog.'
    else:
        return False, "Database error occurred while adding the book."

def borrow_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:

    # validate patron id
    if not re.fullmatch(r"\d{6}", str(patron_id or "")):
        return False, "Invalid patron ID (must be exactly 6 digits)."

    # book exists & availability
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    if book.get("available_copies", 0) <= 0:
        return False, "This book is currently not available."

    # active borrow count
    current_count = get_patron_borrow_count(patron_id) or 0
    if current_count >= 5:
        return False, "You have reached the maximum borrowing limit of 5 books."

    # (optional) prevent duplicate active borrow of same book
    # If your database.py has a helper like patron_has_active_borrow(patron_id, book_id), use it:
    try:
        from database import patron_has_active_borrow  # type: ignore
        if patron_has_active_borrow(patron_id, book_id):
            return False, "You already have this book borrowed."
    except Exception:
        pass  # helper not present; skip this check

    # create borrow record (14-day due)
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=14)
    if not insert_borrow_record(patron_id, book_id, borrow_date, due_date):
        return False, "Database error occurred while creating borrow record."

    # decrement availability
    if not update_book_availability(book_id, -1):
        return False, "Database error occurred while updating book availability."

    return True, f'Successfully borrowed "{book.get("title","")}". Due date: {due_date.strftime("%Y-%m-%d")}.'

def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    
    # If your DB exposes a direct "active borrow" check, use it to validate:
    try:
        from database import get_active_borrow  # type: ignore
        if not get_active_borrow(patron_id, book_id):
            return False, "No active borrow record for this patron/book."
    except Exception:
        # If we don't have a checker, proceed to set a return date; DB layer should fail safely if no row exists.
        pass

    # mark returned
    return_ok = update_borrow_record_return_date(patron_id, book_id, datetime.now())
    if not return_ok:
        return False, "Failed to update borrow record with return date."

    # increment availability
    book = get_book_by_id(book_id)
    if book:
        if not update_book_availability(book_id, +1):
            return False, "Failed to update book availability after return."

    return True, "Return successful."


def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict:
    
    # Try to fetch an active or last borrow record using DB helpers if available
    rec = None
    try:
        from database import get_active_borrow  # type: ignore
        rec = get_active_borrow(patron_id, book_id)
    except Exception:
        pass
    if rec is None:
        try:
            from database import get_last_borrow  # type: ignore
            rec = get_last_borrow(patron_id, book_id)
        except Exception:
            pass

    if not rec:
        return {"status": "not found", "fee": 0.0, "days_overdue": 0}

    borrow_dt = rec.get("borrow_date")
    if isinstance(borrow_dt, str):
        borrow_dt = datetime.fromisoformat(borrow_dt)
    due_dt = borrow_dt + timedelta(days=14)

    today_or_return = rec.get("return_date")
    if isinstance(today_or_return, str):
        today_or_return = datetime.fromisoformat(today_or_return)
    if not today_or_return:
        today_or_return = datetime.now()

    days_over = (today_or_return.date() - due_dt.date()).days
    if days_over <= 0:
        return {"status": "ok", "fee": 0.0, "days_overdue": 0}

    first7 = min(days_over, 7)
    rest = max(0, days_over - 7)
    fee = min(first7 * 0.50 + rest * 1.00, 15.00)
    return {"status": "ok", "fee": round(fee, 2), "days_overdue": days_over}


def search_books_in_catalog(search_term: str, search_type: Optional[str] = None) -> List[Dict]:
   
    q = (search_term or "").strip()
    if not q:
        return []

    books = get_all_books() or []
    t = (search_type or "").strip().lower()

    out: List[Dict] = []
    for b in books:
        title = (b.get("title") or "").lower()
        author = (b.get("author") or "").lower()
        isbn = (b.get("isbn") or "").strip()

        if t in ("", "title"):
            if q.lower() in title:
                out.append(b)
        elif t == "author":
            if q.lower() in author:
                out.append(b)
        elif t == "isbn":
            if q == isbn:  # exact match only
                out.append(b)
        else:
            # unknown type → act like flexible (title/author)
            if q.lower() in title or q.lower() in author:
                out.append(b)
    return out


def get_patron_status_report(patron_id: str) -> Dict:
    import database as db
    from datetime import datetime, timedelta

    current = getattr(db, "get_active_borrows_for_patron", lambda *_: [])(patron_id)
    history = getattr(db, "get_borrows_for_patron", lambda *_: [])(patron_id)

    # compute fees for active items (optional, to show a number)
    total_fees = 0.0
    for rec in current:
        borrow_dt = rec["borrow_date"]
        if isinstance(borrow_dt, str):
            borrow_dt = datetime.fromisoformat(borrow_dt)
        due_dt = borrow_dt + timedelta(days=14)
        days_over = (datetime.now().date() - due_dt.date()).days
        if days_over > 0:
            first7 = min(days_over, 7)
            rest = max(0, days_over - 7)
            fee = min(first7 * 0.50 + rest * 1.00, 15.00)
            total_fees += fee

    return {
        "current": current,
        "count_current": len(current),
        "history": history,
        "total_fees": round(total_fees, 2),
    }
