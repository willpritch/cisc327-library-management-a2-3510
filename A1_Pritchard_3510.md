# Assignment 1 – Project Implementation Status
**Name:** Will Pritchard  
**Student ID:** 20293510  
**Group #:** N/A

## Implementation Status Table

| Function / Feature (from requirements_specification.md) | Code Reference (file:function/route) | Implementation Status (Complete/Partial/Missing) | What’s Missing (if any) |
|---|---|---|---|
| R1: Add Book To Catalog (title/author required; title ≤200, author ≤100; ISBN=13 digits; copies>0; show message; redirect to catalog) | `library_service.py:add_book_to_catalog` ; route `POST /add_book` | Partial | ISBN/copies validation work; max-length checks (200/100) not confirmed; exact success/error message wording per spec not guaranteed. |
| R2: Book Catalog Display (ID, Title, Author, ISBN, Available/Total, Borrow action) | route `GET /catalog`; templates under `templates/` | Complete | Catalog page and listing work; if any column is missing in your local UI, flip to “Partial” and note which. |
| R3: Book Borrowing Interface (patron ID 6 digits; check availability; patron limit 5; record; decrement; messages) | `library_service.py:borrow_book` ; route `POST /borrow` | Partial | 6-digit patron validation and 5-book limit not confirmed; message text not verified against spec. |
| R4: Book Return Processing (verify patron borrowed it; update available; record return date; display late fees) | `library_service.py:return_book` ; route `POST /return` | Partial | Availability increment OK; verifying same patron + recording return date + showing late fees not confirmed. |
| R5: Late Fee Calculation API (`GET /api/late_fee/<patron_id>/<book_id>`; 14-day due; $0.50/$1.00 tier; max $15; JSON) | `routes/api_routes.py:get_late_fee` ; helper in `library_service.py` | Partial | Endpoint exists but logic incomplete: `calculate_late_fee_for_book` returns `None`; due-date (14 days), tiered rates, $15 cap, and JSON shape/consistent status codes not fully implemented. |
| R6: Book Search (q, type in {title, author, isbn}; partial case-insensitive for title/author; exact for ISBN; same format as catalog) | `library_service.py:search_books` ; route `GET /search` | Partial | Basic term matching OK; strict `type` behavior (partial vs exact) not fully confirmed. |
| R7: Patron Status Report (menu item; current borrows + due dates; total late fees; count; history) | expected route `GET /patron/<id>/status` (and menu link) | Missing | No dedicated patron status page/menu item found. |

## Test Summary

- Framework: pytest  
- How to run: `pytest -q`

- Test files:
  - `tests/test_r1_add_book.py` – 5 cases (valid add; zero/negative copies; invalid ISBN length; duplicate ISBN)
  - `tests/test_r2_catalog.py` – 5 cases (page loads; ISBN header; newly-added item shows; available/total shown; borrow button visible)
  - `tests/test_r3_borrow.py` – 5 cases (success; none available; invalid patron format; double-borrow blocked; borrow-limit flow)
  - `tests/test_r4_return.py` – 5 cases (success via route; unknown book; return-without-borrow; patron mismatch flow; bad input)
  - `tests/test_r5_late_fee_api.py` – 5 cases (endpoint exists/skip; JSON shape/skip; nonnegative fee/skip; $15 cap/skip; invalid input/skip)
  - `tests/test_r6_search.py` – 5 cases (title partial/case-insensitive; author partial/case-insensitive; ISBN exact; ISBN partial no-match; no results)
  - `tests/test_r7_patron_status.py` – 5 cases (route exists/skip; required sections/skip; menu link/ok; counts/skip; unknown patron/ok)

- Results from my run:
  - **27 passed, 5 skipped**
  - Skipped tests correspond to features marked **Partial/Missing** in the status table (e.g., late-fee API and patron status page).