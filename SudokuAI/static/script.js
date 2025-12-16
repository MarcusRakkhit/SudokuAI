/* ==========================================================
   ELEMENTS & STATE
   Grab essential DOM elements and initialize state variables
   ========================================================== */
const uploadBtn = document.getElementById("uploadBtn");           // Upload button
const solveBtn = document.getElementById("solveBtn");             // Solve button
const loadingOverlay = document.getElementById("loadingOverlay"); // Full-page loading overlay
const loadingText = document.getElementById("loadingText");       // Text inside loading overlay
const gridContainer = document.getElementById("gridContainer");   // Container for Sudoku grid

let currentGrid = [];      // Current state of the grid (2D array)
let originalMask = [];     // Tracks which cells were detected by OCR initially
let currentKey = null;     // Key assigned by backend for this grid

/* ==========================================================
   LOADING OVERLAY FUNCTIONS
   Show/hide loading overlay and disable/enable buttons
   ========================================================== */
function showLoading(text) {
    loadingText.textContent = text;
    loadingOverlay.classList.remove("hidden");
    uploadBtn.disabled = true;
    solveBtn.disabled = true;
}

function hideLoading() {
    loadingOverlay.classList.add("hidden");
    uploadBtn.disabled = false;
    solveBtn.disabled = false;
}

/* ==========================================================
   GRID VALIDATION
   Check for duplicates in rows, columns, and 3x3 blocks
   ========================================================== */
function validateGrid(grid) {
    const errors = [];

    // Check rows for duplicates
    for (let r = 0; r < 9; r++) {
        const seen = {};
        for (let c = 0; c < 9; c++) {
            const val = grid[r][c];
            if (val === 0) continue;
            if (seen[val]) errors.push(`Duplicate ${val} in row ${r + 1}`);
            else seen[val] = true;
        }
    }

    // Check columns for duplicates
    for (let c = 0; c < 9; c++) {
        const seen = {};
        for (let r = 0; r < 9; r++) {
            const val = grid[r][c];
            if (val === 0) continue;
            if (seen[val]) errors.push(`Duplicate ${val} in column ${c + 1}`);
            else seen[val] = true;
        }
    }

    // Check 3x3 blocks for duplicates
    for (let br = 0; br < 3; br++) {
        for (let bc = 0; bc < 3; bc++) {
            const seen = {};
            for (let r = br * 3; r < br * 3 + 3; r++) {
                for (let c = bc * 3; c < bc * 3 + 3; c++) {
                    const val = grid[r][c];
                    if (val === 0) continue;
                    if (seen[val]) errors.push(`Duplicate ${val} in block (${br + 1},${bc + 1})`);
                    else seen[val] = true;
                }
            }
        }
    }

    return errors; // Array of error strings
}

/* ==========================================================
   RENDER GRID
   Build HTML table for Sudoku grid with inputs
   Handles both editable (before solve) and solved (readonly) states
   ========================================================== */
function renderGrid(grid, solved = false) {
    // Clone grid to state
    currentGrid = grid.map(row => row.slice());
    gridContainer.innerHTML = "";

    // Track which cells were originally OCR-detected
    // When we render the grid, we only orignal OCR cells written in bold
    if (!solved) {
        originalMask = grid.map(row => row.map(val => val !== 0));
    }

    // Create table element for Sudoku grid
    const table = document.createElement("table");
    table.className = "sudoku";

    // Populate table with inputs
    grid.forEach((row, r) => {
        const tr = document.createElement("tr");

        row.forEach((val, c) => {
            const td = document.createElement("td");
            const input = document.createElement("input");

            input.type = "text";
            input.maxLength = 1;
            input.value = val === 0 ? "" : val;

            if (!solved) {
                // Editable inputs
                input.addEventListener("input", () => {
                    const v = parseInt(input.value);
                    currentGrid[r][c] = isNaN(v) ? 0 : v;
                });
                // Highlight original OCR numbers
                if (originalMask[r][c]) input.classList.add("fixed");
            } else {
                // Solved inputs (AI-generated numbers are highlighted)
                if (!originalMask[r][c]) input.classList.add("solved");
                input.disabled = true;
            }

            td.appendChild(input);
            tr.appendChild(td);
        });

        table.appendChild(tr);
    });

    gridContainer.appendChild(table);

    // Show instructions below grid for editable state
    if (!solved) showGridInstructions();
}

/* ==========================================================
   UPLOAD IMAGE HANDLER
   --------------------
   Handles the "Upload & Extract" button click:
   1. Checks if the user has selected a file.
   2. Sends the selected image to the python code (/upload endpoint).
   3. Receives the OCR-detected Sudoku grid from the backend.
   4. Updates the front-end grid display for review and editing.
   ========================================================== */
uploadBtn.addEventListener("click", async () => {
    // Get the file input element
    const fileInput = document.getElementById("sudokuImage");

    // Ensure a file has been selected
    if (!fileInput.files.length) {
        alert("Please select an image first.");
        return;
    }

    // Prepare FormData to send the image file in the POST request
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    try {
        // Show loading overlay with message
        showLoading("Extracting Sudoku grid…");

        // Send the file to main.py for OCR extraction
        const res = await fetch("/upload", {
            method: "POST",
            body: formData
        });

        // Parse the JSON response from main.py
        const data = await res.json();

        // Hide loading overlay after response
        hideLoading();

        // Handle any backend error (e.g., invalid image or OCR failure)
        if (data.error) {
            alert(data.error);
            return;
        }

        // Save the unique key returned by backend to track this grid session
        currentKey = data.key;

        // Copy the returned grid into the front-end state (deep copy)
        currentGrid = data.grid.map(row => row.slice());

        // Render the grid for user review and editing
        renderGrid(currentGrid, false);

    } catch (err) {
        // Hide loading overlay and alert the user if an exception occurs
        hideLoading();
        alert("Failed to process image.");
        console.error("Upload error:", err);
    }
});

/* ==========================================================
   SOLVE GRID HANDLER
   ------------------
   Handles the "Solve Sudoku" button click:
   1. Validates that a grid has been uploaded and reviewed.
   2. Checks for duplicates in rows, columns, and blocks.
   3. Sends the grid to the python code (/solve endpoint) for solving.
   4. Receives the solved grid and updates the table.
   5. Distinguishes AI-solved numbers from original OCR numbers.
   ========================================================== */
solveBtn.addEventListener("click", async () => {
    // Ensure a grid exists and a key is available
    if (!currentGrid || !currentKey) {
        alert("Please upload and verify the grid first.");
        return;
    }

    // Validate the current grid for duplicates before sending to solver
    const validationErrors = validateGrid(currentGrid);
    if (validationErrors.length > 0) {
        alert(
            "Cannot solve! Fix the following duplicates first:\n" +
            validationErrors.join("\n")
        );
        return;
    }

    // Show loading overlay while solver works
    showLoading("Solving Sudoku…");

    try {
        // Prepare payload with current key and grid
        const payload = { key: currentKey, grid: currentGrid };

        // Send POST request to main.py solve endpoint
        const res = await fetch("/solve", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        // Parse the solved grid from main.py
        const data = await res.json();

        // Hide loading overlay after response
        hideLoading();

        // Handle any solver errors returned from backend
        if (data.error) {
            alert(data.error);
            return;
        }

        // Update front-end grid state with solved grid
        currentGrid = data.solved_grid.map(row => row.slice());

        // Render solved grid; highlight AI-generated numbers distinctly
        renderGrid(currentGrid, true);

    } catch (err) {
        // Hide overlay and log error if fetch fails
        hideLoading();
        alert("Failed to solve Sudoku.");
        console.error("Solve error:", err);
    }
});

/* ==========================================================
   DISPLAY GRID INSTRUCTIONS
   Shows professional, clean instructions below the grid
   ========================================================== */
function showGridInstructions() {
    const container = document.getElementById("gridInstructions");
    container.innerHTML = `
        <p class="hint strong"><strong>How to Edit the Sudoku Grid:</strong></p>
        <ul class="grid-rules">
            <li><strong>Click a cell:</strong> Type a number (1–9).</li>
            <li><strong>Empty cells:</strong> Leave blank or enter 0.</li>
            <li><strong>Original numbers:</strong> Highlighted in gray, editable if needed.</li>
            <li><strong>No duplicates:</strong> Ensure rows, columns, and 3×3 blocks have unique numbers.</li>
            <li><strong>Standard rules:</strong> Each number 1–9 must appear exactly once per row, column, and 3×3 block.</li>
            <li><strong>Solve:</strong> Press <strong>“Solve Sudoku”</strong> to fill remaining cells automatically.</li>
        </ul>
    `;
}