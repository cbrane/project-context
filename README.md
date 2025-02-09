# project-context - Project to Markdown Converter

From your terminal, copy the current project folder you're in as context, so you can pass it to an LLM like o1-pro, o3-mini-high, or others that use a chat interface. 

This project contains a script that recursively converts your project structure and file contents into a Markdown document. The final Markdown output is wrapped in XML `<project>` tags, making it easy to pass as context to your LLM.

## How It Works

- **Recursive Directory Traversal:**  
  The script walks through your project directory recursively, building a tree structure while applying `.gitignore` rules.

- **File Processing:**  
  - **Text Files:** Their contents are rendered in fenced code blocks with syntax highlighting based on file extension.  
  - **Binary Files:** The script notes that these files are binary and does not include their content.

- **XML Tag Wrapping:**  
  Once the Markdown is generated, it is automatically wrapped in `<project>` and `</project>` tags.

- **Clipboard Integration:**  
  The final Markdown is copied to your clipboard using `pbcopy` for easy pasting elsewhere.

- **Token Counting:**  
  After wrapping the Markdown output in `<project>` tags, the script counts the total number of tokens in the document (using `tiktoken` if available, or a fallback method) and prints the token count to the console. This helps you understand how much context is being passed to your LLM.

## Setup Instructions

Follow these steps to set up and use the script:

### 1. Create a Dedicated Scripts Folder (If You Haven’t Already)

You mentioned you already have `~/scripts` in your PATH. If not, follow these steps:

```bash
mkdir -p ~/scripts
echo 'export PATH="$HOME/scripts:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### 2. Create a Virtual Environment for Your Scripts

Inside `~/scripts`, create a virtual environment. For example:

```bash
cd ~/scripts
python3 -m venv .venv
```

This command creates a folder called `.venv` in `~/scripts`. The interpreter at `.venv/bin/python` will have its own separate packages.

### 3. Activate the Virtual Environment and Install Dependencies

Activate the virtual environment and install the required dependencies:

```bash
source ~/scripts/.venv/bin/activate
pip install --upgrade pip
pip install pathspec
```

This installs the `pathspec` package into your dedicated environment.

### 4. Update the Shebang in `project_to_md.py`

Edit your `project_to_md.py` script so that the first line (the shebang) points directly to the Python interpreter in your new `.venv`. For example:

```bash
#!/Users/connorraney/scripts/.venv/bin/python
```

> **Important:** Adjust the path if your username or folder structure is different. Make sure it correctly points to your `.venv/bin/python`.

### 5. Make Sure the Script is Executable

Ensure that the script has executable permissions:

```bash
chmod +x ~/scripts/project_to_md.py
```

### 6. Confirm It Runs Anywhere

Open a new terminal window or run:

```bash
source ~/.zshrc
```

Then, navigate to any project directory (for example):

```bash
cd ~/some_project
```

Run the script by simply typing:

```bash
project_to_md.py
```

Since `~/scripts` is in your PATH, the shell will find `project_to_md.py` and run it using the Python interpreter in your `.venv`.

## Why This Setup Works

- **Shebang Points to One Specific Python:**  
  By using a specific shebang like `#!/Users/connorraney/scripts/.venv/bin/python`, the script always runs under that interpreter, regardless of the current directory or active Python version.

- **Local Virtual Environment:**  
  The `.venv` in `~/scripts` is separate from your project-specific environments. This means installing or removing packages in your project venv won’t affect this global scripts environment, and vice versa.

- **Ease of Use via PATH:**  
  With `~/scripts` added to your PATH, you can run `project_to_md.py` from anywhere without specifying its full path.

## Usage

After setting up, simply navigate to any project folder and run:

```bash
project_to_md.py
```

The script will generate a Markdown representation of your project (wrapped in `<project>` XML tags), count the total number of tokens in the output, and copy the Markdown to your clipboard.