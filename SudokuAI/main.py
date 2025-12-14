import sys
from app.StoreCells import StoreCells
from app.PrintGrid import PrintGrid
from app.Backtracking import Backtracking
from NeuralNetwork import SudokuImageToGrid
    

# To run the code in a terminal console type 'docker run -it sudokuai python main.py'
# In cmd docker run -it -v "[Image Source Absolute location]":/app/image sudokuai python main.py /app/image/[image File]

def main():      
    # Replace with your image path
    image_path = sys.argv[1]

    while True:
        print("\n" + "-"*50)
        print("SUDOKU IMAGE PROCESSOR")
        print("-"*50)
        
        try:
            print(f"\nProcessing image: {image_path}")
            grid = SudokuImageToGrid.extract_sudoku_grid(image_path)
            
            print("\nExtracted grid:")
            SudokuImageToGrid.print_sudoku_grid(grid)
            
            result = SudokuImageToGrid.edit_grid_interactive(grid, image_path)
            
            grid = result

            CellObjectCreator = StoreCells()
            grid = CellObjectCreator.createList(grid)
            
            # Prints the initial sudoku state
            console_printer = PrintGrid()
            print("\n---SOLVING PUZZLE---\n")

            search2 = Backtracking()
            search2.add_first(grid)
            grid = search2.backtracker_search()

            console_printer.print_numbers(grid)

            break
                
        except Exception as e:
            print(f"\nError processing image: {e}")
            import traceback
            traceback.print_exc()
            break


if __name__ == "__main__":
    main()
        