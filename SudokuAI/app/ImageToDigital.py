import cv2
import numpy as np
import pytesseract


# ============================================================
# TESSERACT SETUP
# ============================================================
# Explicitly specifies the Tesseract OCR executable path.
# Required on Windows systems where Tesseract is not
# automatically available via the system PATH.
#
# For cross-platform or production deployments, this should
# be configured using environment variables instead.
# ============================================================

#pytesseract.pytesseract.tesseract_cmd = (
    #r"C:\Program Files\Tesseract-OCR\tesseract.exe"
#)


# ============================================================
# SUDOKU IMAGE → DIGITAL GRID PROCESSOR
# ============================================================
# Responsibilities:
# - Detect the Sudoku board within an image
# - Segment the board into individual cells
# - Recognize digits using OCR
# - Validate the resulting grid against Sudoku rules
#
# Output:
# - 9×9 integer grid
# - 0 indicates an empty cell
# ============================================================

class SudokuImageToGrid:

    # ========================================================
    # OCR-BASED GRID EXTRACTION
    # ========================================================
    @staticmethod
    def extract_sudoku_grid(image_path):
        """
        Converts a Sudoku image into a 9×9 digital grid using
        OpenCV for image processing and Tesseract for OCR.

        Parameters
        ----------
        image_path : str
            Path to the input Sudoku image.
        existing_grid : list[list[int]] | None
            Optional grid used as a base. Pre-filled values
            are preserved and not overwritten by OCR.

        Returns
        -------
        list[list[int]]
            Extracted Sudoku grid.
        """

        # ----------------------------------------------------
        # Load image and convert to grayscale
        # ----------------------------------------------------
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # ----------------------------------------------------
        # Apply binary inversion thresholding
        # Highlights digits and grid lines for contour detection
        # ----------------------------------------------------
        _, thresh = cv2.threshold(
            gray, 128, 255, cv2.THRESH_BINARY_INV
        )

        # ----------------------------------------------------
        # Locate the Sudoku board using contour detection
        # ----------------------------------------------------
        contours, _ = cv2.findContours(
            thresh,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        # Assume the largest detected contour is the Sudoku grid
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)

        # ----------------------------------------------------
        # Initialize output grid
        # ----------------------------------------------------
        sudoku_grid = [[0 for _ in range(9)] for _ in range(9)]

        # Estimate individual cell dimensions
        cell_h = h // 9
        cell_w = w // 9

        # ----------------------------------------------------
        # Process each cell independently
        # ----------------------------------------------------
        for row in range(9):
            for col in range(9):

                # Calculate pixel region for the current cell
                cell_y = y + row * cell_h
                cell_x = x + col * cell_w

                # Crop with padding to remove grid lines
                padding = 5
                cell = gray[
                    cell_y + padding: cell_y + cell_h - padding,
                    cell_x + padding: cell_x + cell_w - padding
                ]

                # Threshold cell for OCR processing
                _, cell_thresh = cv2.threshold(
                    cell, 128, 255, cv2.THRESH_BINARY_INV
                )

                # ------------------------------------------------
                # Heuristic check to determine if the cell
                # likely contains a digit (non-empty)
                # ------------------------------------------------
                if np.sum(cell_thresh) > 100:

                    # OCR configuration:
                    # - psm 10 (Page Segmentation Mode 10): There's a single character recognition
                    # - tessedit_char_whitelist will restrict output to digits 1–9
                    config = (
                        "--psm 10 --oem 3 "
                        "-c tessedit_char_whitelist=123456789"
                    )

                    text = pytesseract.image_to_string(
                        cell, config=config
                    ).strip()

                    # Adds a number to the grid if it's a digit
                    if text.isdigit():
                        sudoku_grid[row][col] = int(text)

        return sudoku_grid


    # ========================================================
    # GRID VALIDATION (SUDOKU CONSTRAINTS)
    # ========================================================
    @staticmethod
    def validate_no_duplicates(grid):
        """
        Validates the grid against Sudoku rules by checking
        for duplicate values in rows, columns, and 3×3 blocks.

        Returns
        -------
        list[str]
            Descriptive error messages for detected conflicts.
        """

        errors = []

        # ----------------------
        # Validate rows
        # ----------------------
        for r in range(9):
            seen = {}
            for c in range(9):
                val = grid[r][c]
                if val != 0:
                    if val in seen:
                        errors.append(
                            f"Duplicate {val} in row {r} "
                            f"(cols {seen[val]} and {c})"
                        )
                    else:
                        seen[val] = c

        # ----------------------
        # Validate columns
        # ----------------------
        for c in range(9):
            seen = {}
            for r in range(9):
                val = grid[r][c]
                if val != 0:
                    if val in seen:
                        errors.append(
                            f"Duplicate {val} in column {c} "
                            f"(rows {seen[val]} and {r})"
                        )
                    else:
                        seen[val] = r

        # ----------------------
        # Validate 3×3 subgrids
        # ----------------------
        for br in range(3):
            for bc in range(3):
                seen = {}
                for r in range(br * 3, br * 3 + 3):
                    for c in range(bc * 3, bc * 3 + 3):
                        val = grid[r][c]
                        if val != 0:
                            if val in seen:
                                pr, pc = seen[val]
                                errors.append(
                                    f"Duplicate {val} in block ({br},{bc}) "
                                    f"at ({pr},{pc}) and ({r},{c})"
                                )
                            else:
                                seen[val] = (r, c)

        return errors


    @staticmethod
    def count_filled_cells(grid):
        """
        Returns the number of non-empty cells in the grid.
        """
        return sum(
            1 for r in range(9)
            for c in range(9)
            if grid[r][c] != 0

        )
