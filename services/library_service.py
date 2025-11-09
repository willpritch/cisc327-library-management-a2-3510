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
    

    existing = get_book_by_isbn(isbn)
    if existing:
        return False, "A book with this ISBN already exists."
    
    success = insert_book(title.strip(), author.strip(), isbn, total_copies, total_copies)
    if success:
        return True, f'Book "{title.strip()}" has been successfully added to the catalog.'
    else:
        return False, "Database error occurred while adding the book."

def borrow_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:


    if not re.fullmatch(r"\d{6}", str(patron_id or "")):
        return False, "Invalid patron ID (must be exactly 6 digits)."

    
    book = get_book_by_id(book_id)
    if not book:
        return False, "Book not found."
    if book.get("available_copies", 0) <= 0:
        return False, "This book is currently not available."

  
    current_count = get_patron_borrow_count(patron_id) or 0
    if current_count >= 5:
        return False, "You have reached the maximum borrowing limit of 5 books."

    
    try:
        from database import patron_has_active_borrow  
        if patron_has_active_borrow(patron_id, book_id):
            return False, "You already have this book borrowed."
    except Exception:
        pass  

    
    borrow_date = datetime.now()
    due_date = borrow_date + timedelta(days=14)
    if not insert_borrow_record(patron_id, book_id, borrow_date, due_date):
        return False, "Database error occurred while creating borrow record."

    if not update_book_availability(book_id, -1):
        return False, "Database error occurred while updating book availability."

    return True, f'Successfully borrowed "{book.get("title","")}". Due date: {due_date.strftime("%Y-%m-%d")}.'

def return_book_by_patron(patron_id: str, book_id: int) -> Tuple[bool, str]:
    
    
    try:
        from database import get_active_borrow  
        if not get_active_borrow(patron_id, book_id):
            return False, "No active borrow record for this patron/book."
    except Exception:
        pass
    
    return_ok = update_borrow_record_return_date(patron_id, book_id, datetime.now())
    if not return_ok:
        return False, "Failed to update borrow record with return date."
    book = get_book_by_id(book_id)
    if book:
        if not update_book_availability(book_id, +1):
            return False, "Failed to update book availability after return."

    return True, "Return successful."


def calculate_late_fee_for_book(patron_id: str, book_id: int) -> Dict:
    rec = None
    try:
        from database import get_active_borrow  
        rec = get_active_borrow(patron_id, book_id)
    except Exception:
        pass
    if rec is None:
        try:
            from database import get_last_borrow  
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
            if q == isbn:  
                out.append(b)
        else:
            if q.lower() in title or q.lower() in author:
                out.append(b)
    return out


def get_patron_status_report(patron_id: str) -> Dict:
    import database as db
    from datetime import datetime, timedelta

    current = getattr(db, "get_active_borrows_for_patron", lambda *_: [])(patron_id)
    history = getattr(db, "get_borrows_for_patron", lambda *_: [])(patron_id)

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
    
    # --- NEW FOR A3 ---

def pay_late_fees(patron_id: str, book_id: int, payment_gateway) -> tuple[bool, str]:
    
    if not patron_id or not str(patron_id).isdigit():
        return False, "Invalid patron ID."
    fee_info = calculate_late_fee_for_book(patron_id, book_id)
    if not fee_info or fee_info.get("fee", 0) <= 0:
        return False, "No late fee to pay."

    try:
        result = payment_gateway.process_payment(patron_id, fee_info["fee"])
        if result and result.get("status") == "success":
            return True, "Payment successful."
        return False, "Payment declined."
    except Exception as e:
        return False, f"Error: {e}"

def refund_late_fee_payment(transaction_id: str, amount: float, payment_gateway) -> tuple[bool, str]:
    """
    Call payment_gateway.refund_payment(transaction_id, amount) with basic guards.
    Returns (ok, message).
    """
    if not transaction_id:
        return False, "Invalid transaction ID."
    if amount is None or amount <= 0 or amount > 15:
        return False, "Invalid refund amount."

    try:
        result = payment_gateway.refund_payment(transaction_id, amount)
        if result and result.get("status") == "refund_success":
            return True, "Refund successful."
        return False, "Refund declined."
    except Exception as e:
        return False, f"Error: {e}"

