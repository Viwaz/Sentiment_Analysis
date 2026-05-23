import json
import pathlib
import sys

# Load notebooks/07_active_learning.ipynb
nb_path = pathlib.Path('notebooks/07_active_learning.ipynb')
with open(nb_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Extract code cells
code_cells = [cell for cell in nb['cells'] if cell['cell_type'] == 'code']

# Monkeypatch pathlib.Path.cwd and flavor-specific cwd methods
original_cwd = pathlib.Path.cwd

@classmethod
def mock_cwd(cls):
    # Ensure it returns the notebooks subdirectory of the actual project root
    real_cwd = original_cwd()
    if real_cwd.name == 'notebooks':
        return real_cwd
    return real_cwd / 'notebooks'

pathlib.Path.cwd = mock_cwd
if hasattr(pathlib, 'WindowsPath'):
    pathlib.WindowsPath.cwd = mock_cwd
if hasattr(pathlib, 'PosixPath'):
    pathlib.PosixPath.cwd = mock_cwd

# Run each code cell sequentially
globals_dict = {}

# Mock sys.argv to prevent argparse issues if any imports parse arguments
sys.argv = ['ipython'] 

print("Running notebook code cells programmatically...")
for i, cell in enumerate(code_cells):
    code_text = "".join(cell['source'])
    print(f"\n--- Running Cell {i+1} ---")
    
    # We do not want block plt.show() from running and waiting for user input
    if "plt.show()" in code_text:
        code_text = code_text.replace("plt.show()", "pass")
    
    try:
        exec(code_text, globals_dict)
        print(f"Cell {i+1} ran successfully.")
    except Exception as e:
        print(f"Error in Cell {i+1}: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

print("\nAll notebook cells executed successfully!")
