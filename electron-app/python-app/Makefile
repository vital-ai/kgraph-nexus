CONDA_ENV = kgraph-nexus

# Define the paths for PyInstaller and assets
PYINSTALLER = pyinstaller
SCRIPT = app.py
SPEC_FILE = app.spec

# Activate Conda environment and install dependencies
.PHONY: setup
setup:
	@echo "Setting up Conda environment and installing dependencies..."
	conda run -n $(CONDA_ENV) pip install -r requirements.txt
	conda run -n $(CONDA_ENV) pip install pyinstaller

# Build the Python executable
.PHONY: build-python
build-python: setup
	@echo "Building Python executable with PyInstaller..."
	conda run -n $(CONDA_ENV) $(PYINSTALLER) $(SPEC_FILE)
	@echo "Python app built successfully."

# Clean the build artifacts
.PHONY: clean
clean:
	@echo "Cleaning up build artifacts..."
	rm -rf build dist
	@echo "Clean up done."