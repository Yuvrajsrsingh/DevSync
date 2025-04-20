import ast
import os
import sys 
import re
from transformers import pipeline
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn", use_fast=False)


def get_code_files(directory, extensions=[".py", ".js", ".cpp", ".java"]):
    """Find all code files in the given directory and subdirectories."""
    code_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                code_files.append(os.path.join(root, file))
    return code_files

def extract_python_info(file_path):
    """Extract class, function names, and AI-powered summary from a Python file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        tree = ast.parse(content, filename=file_path)
    
    classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    summary = generate_ai_summary(content)

    return {"file": file_path, "classes": classes, "functions": functions, "summary": summary}


def extract_js_cpp_info(file_path):
    """Extract class, function names, and AI-powered summary from JavaScript & C++ files."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Regex patterns
    class_pattern = r"\bclass\s+(\w+)"
    function_pattern = r"\b(?:function\s+|[a-zA-Z_]\w*\s*\()\s*(\w+)\s*\("

    classes = re.findall(class_pattern, content)
    functions = re.findall(function_pattern, content)
    summary = generate_ai_summary(content)

    return {"file": file_path, "classes": classes, "functions": functions, "summary": summary}

def generate_markdown_summary(code_info, output_file="DevSync.md"):
    """Generate a Markdown summary of the extracted codebase info, including AI-powered summaries."""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# CodeMap Summary (AI-Powered) 🤖\n\n")
        
        for item in code_info:
            f.write(f"## {os.path.basename(item['file'])}\n")
            f.write(f"📂 **Path:** `{item['file']}`\n\n")

            if item["classes"]:
                f.write("### Classes\n")
                for cls in item["classes"]:
                    f.write(f"- `{cls}`\n")
            
            if item["functions"]:
                f.write("\n### Functions\n")
                for func in item["functions"]:
                    f.write(f"- `{func}`\n")

            f.write("\n### AI-Powered Summary 📜\n")
            f.write(f"📝 {item['summary']}\n\n")
            f.write("\n---\n")

    print("✅ AI-powered code summary generated in DevSync.md!")


def search_codebase(code_info, search_term):
    """Search for a function/class in the extracted codebase."""
    results = []
    for item in code_info:
        if search_term in item["classes"] or search_term in item["functions"]:
            results.append(item["file"])
    
    return results

# Load summarization model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def generate_ai_summary(content):
    """Generate AI-powered summary of a given code file content."""
    if len(content.split()) < 50:
        return "Code is too short for meaningful summarization."
    
    content = content[:1024]  
    summary = summarizer(content, max_length=100, min_length=30, do_sample=False)
    return summary[0]["summary_text"]

if __name__ == "__main__":
    files = get_code_files(".", [".py", ".js", ".cpp", ".java"])  
    code_info = []

    for file in files:
        if file.endswith(".py"):
            code_info.append(extract_python_info(file))
        elif file.endswith((".js", ".cpp", ".java")):
            code_info.append(extract_js_cpp_info(file))

    if len(sys.argv) > 1:
        search_term = sys.argv[1]
        results = search_codebase(code_info, search_term)
        if results:
            print(f"🔍 Found `{search_term}` in:")
            for res in results:
                print(f"- {res}")
        else:
            print(f"❌ `{search_term}` not found in the codebase.")
    else:
        generate_markdown_summary(code_info)
        print("✅ Code summary generated in DevSync.md!")
