import os
import uuid

from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.StoreCells import StoreCells
from app.Backtracking import Backtracking
from app.ImageToDigital import SudokuImageToGrid


#note: python -m uvicorn app.main:app --reload

# ============================================================
# FASTAPI APPLICATION SETUP FOR THE WEBSITE
# ============================================================

app = FastAPI()

# Serve static assets (CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure Jinja2 for HTML templating
templates = Jinja2Templates(directory="templates")


# ============================================================
# IN-MEMORY GRID STORAGE
# ============================================================
# Stores Sudoku grids temporarily using a UUID key.
# This allows each user/session to safely modify their grid
# without interfering with others.
#
# NOTE:
# - This is suitable for development and small-scale usage.
# - In production, this should be replaced with a database
#   or cache (e.g. Redis).
# ============================================================

GRIDS: dict[str, list[list[int]]] = {}


# ============================================================
# HOME PAGE
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Render the main application page.

    This endpoint serves the HTML interface where users can:
    - Upload a Sudoku image
    - Edit extracted values
    - Solve the puzzle

    sudoku.html is the main page file.
    """
    return templates.TemplateResponse(
        "sudoku.html",
        {"request": request}
    )


# ============================================================
# UPLOAD SUDOKU IMAGE & OCR EXTRACTION
# ============================================================

@app.post("/upload")
async def upload_sudoku(file: UploadFile = File(...)):
    """
    Accepts an uploaded Sudoku image, saves it locally,
    and extracts a 9x9 grid using OCR and image processing.

    Returns:
    - grid: Extracted Sudoku grid (9x9 list of integers)
    - key: Unique identifier used to track this grid
    """

    # Ensure upload directory exists
    os.makedirs("uploads", exist_ok=True)

    # Save uploaded image to disk
    image_path = os.path.join("uploads", file.filename)
    with open(image_path, "wb") as f:
        f.write(await file.read())

    # Perform OCR + grid extraction
    grid = SudokuImageToGrid.extract_sudoku_grid(image_path)

    # Generate a unique key for this grid
    key = str(uuid.uuid4())
    GRIDS[key] = grid

    return {
        "grid": grid,
        "key": key
    }


# ============================================================
# UPDATE A SINGLE CELL (USER EDITING)
# When we solve a puzzle, we want to reflect any user edits
# to the grid before solving.
# ============================================================

@app.post("/update_cell")
async def update_cell(data: dict):
    """
    Updates a single cell in the stored Sudoku grid.

    Expected JSON body:
    {
        "key": "<uuid>",
        "row": int,
        "col": int,
        "value": int
    }

    Returns:
    - Updated grid
    - Validation errors (duplicate conflicts)
    - Count of filled cells
    """

    key = data.get("key")
    row = int(data.get("row"))
    col = int(data.get("col"))
    value = int(data.get("value"))

    # Retrieve grid using session key
    grid = GRIDS.get(key)
    if not grid:
        return JSONResponse(
            {"error": "Grid not found"},
            status_code=404
        )

    # Update the selected cell
    grid[row][col] = value

    return {
        "grid": grid,
        "errors": SudokuImageToGrid.validate_no_duplicates(grid),
        "filled_count": SudokuImageToGrid.count_filled_cells(grid)
    }


# ============================================================
# SOLVE SUDOKU USING BACKTRACKING
# ============================================================

@app.post("/solve")
async def solve_sudoku(data: dict):
    """
    Solves the Sudoku puzzle using a backtracking algorithm.

    Expected JSON body:
    {
        "key": "<uuid>",
        "grid": [[int, ...], ...]  # 9x9 grid reflecting user edits
    }

    Returns:
    - solved_grid: Completed Sudoku grid
    """

    grid = data.get("grid")

    # Validate grid structure
    if not grid or len(grid) != 9 or any(len(row) != 9 for row in grid):
        return JSONResponse(
            {"error": "Invalid grid"},
            status_code=400
        )

    # --------------------------------------------------------
    # Convert integer grid into Cell objects
    # --------------------------------------------------------
    cell_creator = StoreCells()
    cell_grid = cell_creator.createList(grid)

    # --------------------------------------------------------
    # Solve using backtracking search
    # --------------------------------------------------------
    solver = Backtracking()
    solver.add_first(cell_grid)
    solved_cells = solver.backtracker_search()

    # --------------------------------------------------------
    # Convert solved Cell objects back to integers
    # --------------------------------------------------------
    solved_grid = [
        [
            int(solved_cells[r * 9 + c].get_cell_number())
            if solved_cells[r * 9 + c].get_cell_number() != "."
            else 0
            for c in range(9)
        ]
        for r in range(9)
    ]

    # Optional cleanup to free memory
    key = data.get("key")
    if key in GRIDS:
        del GRIDS[key]

    return {
        "solved_grid": solved_grid
    }