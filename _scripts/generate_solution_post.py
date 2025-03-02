#!/usr/bin/env python3
"""
Script to analyze LeetCode solution files in Python, Java, and Go and generate blog posts
with detailed explanations.
"""

import os
import re
import sys
import glob
import yaml
import time
import json
import frontmatter
from datetime import datetime
from pathlib import Path
import openai
from typing import Dict, List, Tuple, Optional

# Set up OpenAI client
openai.api_key = os.environ.get("OPENAI_API_KEY")
if not openai.api_key:
    print("Error: OPENAI_API_KEY environment variable not set")
    sys.exit(1)

# Configuration
SOLUTIONS_DIR = "."  # Root directory to scan for solutions
OUTPUT_DIR = "_solutions"  # Jekyll collection for solutions

# LeetCode problem patterns in comments for different languages
# Python: # LeetCode #123: Two Sum (Easy) - https://leetcode.com/problems/two-sum/
# Java: // LeetCode #123: Two Sum (Easy) - https://leetcode.com/problems/two-sum/
# Go: // LeetCode #123: Two Sum (Easy) - https://leetcode.com/problems/two-sum/
LEETCODE_PATTERN = re.compile(
    r"(?:#|\/\/)\s*LeetCode\s*#?(\d+)?:?\s*([^(\n]+)(?:\s*\(([^)]+)\))?\s*(?:-\s*)?(?:https?://leetcode\.com/problems/([^/\s]+))?",
    re.IGNORECASE,
)

def ensure_dir(directory: str) -> None:
    """Ensure directory exists."""
    Path(directory).mkdir(parents=True, exist_ok=True)

def get_language_from_file(file_path: str) -> str:
    """Determine programming language from file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".py":
        return "python"
    elif ext == ".java":
        return "java"
    elif ext == ".go":
        return "go"
    else:
        return "unknown"

def extract_problem_info(file_path: str) -> Optional[Dict]:
    """Extract LeetCode problem information from solution file."""
    with open(file_path, "r") as f:
        content = f.read()
    
    # Look for LeetCode problem pattern in comments
    match = LEETCODE_PATTERN.search(content)
    if not match:
        print(f"Warning: Could not find LeetCode info in {file_path}")
        return None
    
    problem_number = match.group(1)
    title = match.group(2).strip()
    difficulty = match.group(3) if match.group(3) else "Medium"  # Default to Medium if not specified
    problem_slug = match.group(4) if match.group(4) else title.lower().replace(" ", "-")
    
    # Determine language and extract code
    language = get_language_from_file(file_path)
    solution_code = extract_code_by_language(content, language)
    
    return {
        "file_path": file_path,
        "problem_number": problem_number,
        "title": title,
        "difficulty": difficulty,
        "problem_slug": problem_slug,
        "leetcode_url": f"https://leetcode.com/problems/{problem_slug}/",
        "code": solution_code,
        "language": language,
    }

def extract_code_by_language(content: str, language: str) -> str:
    """Extract code based on the programming language, removing comments."""
    if language == "python":
        return extract_python_code(content)
    elif language == "java":
        return extract_java_code(content)
    elif language == "go":
        return extract_go_code(content)
    else:
        # Default fallback, just return the content
        return content

def extract_python_code(content: str) -> str:
    """Extract Python code, removing comments."""
    code_lines = []
    in_comment_block = False
    
    for line in content.split("\n"):
        if line.startswith('"""') or line.startswith("'''"):
            in_comment_block = not in_comment_block
            continue
        
        if not in_comment_block and not line.strip().startswith("#"):
            code_lines.append(line)
    
    return "\n".join(code_lines).strip()

def extract_java_code(content: str) -> str:
    """Extract Java code, removing comments."""
    # Remove multi-line comments
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # Remove single line comments
    code_lines = []
    for line in content.split("\n"):
        # Remove single-line comments
        if "//" in line:
            line = line.split("//")[0]
        if line.strip():
            code_lines.append(line)
    
    return "\n".join(code_lines).strip()

def extract_go_code(content: str) -> str:
    """Extract Go code, removing comments."""
    # Remove multi-line comments
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # Remove single line comments
    code_lines = []
    for line in content.split("\n"):
        # Remove single-line comments
        if "//" in line:
            line = line.split("//")[0]
        if line.strip():
            code_lines.append(line)
    
    return "\n".join(code_lines).strip()

def generate_explanation(solution_info: Dict) -> Dict:
    """Generate detailed explanation using OpenAI API."""
    language = solution_info['language']
    
    prompt = f"""
# LeetCode Problem: {solution_info['title']}
Problem #{solution_info['problem_number']} - {solution_info['difficulty']}

## Code Solution ({language.capitalize()}):
```{language}
{solution_info['code']}
```

Please provide a comprehensive analysis of this LeetCode solution including:
1. A concise problem statement based on the code and title
2. The approach/algorithm used to solve the problem 
3. A detailed line-by-line explanation of how the code works
4. Time and space complexity analysis

Format your response as a JSON object with these keys:
- problem_statement (markdown string)
- approach (markdown string)
- explanation (markdown string)
- time_complexity (string, e.g., "O(n)")
- space_complexity (string, e.g., "O(n)")

Keep your response brief but informative, focusing on the key insights.
"""

    retries = 3
    while retries > 0:
        try:
            response = openai.chat.completions.create(
                model="gpt-4-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                response_format={"type": "json_object"},
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            retries -= 1
            print(f"Error calling OpenAI API: {e}. Retries left: {retries}")
            if retries > 0:
                time.sleep(5)  # Wait before retrying
            else:
                raise

def determine_tags(solution_info: Dict) -> List[str]:
    """Determine tags based on the solution code and language."""
    tags = []
    code_lower = solution_info['code'].lower()
    language = solution_info['language']
    
    # Add language tag
    tags.append(language.capitalize())
    
    # Add algorithm tags based on code content
    if "dynamic programming" in code_lower or "dp" in code_lower:
        tags.append("Dynamic Programming")
    elif "breadth first" in code_lower or "bfs" in code_lower:
        tags.append("BFS")
    elif "depth first" in code_lower or "dfs" in code_lower:
        tags.append("DFS")
    elif "binary search" in code_lower:
        tags.append("Binary Search")
    elif "two pointer" in code_lower:
        tags.append("Two Pointers")
    elif "backtrack" in code_lower:
        tags.append("Backtracking")
    
    # Add data structure tags - language agnostic patterns
    if "tree" in code_lower or ("node" in code_lower and "left" in code_lower and "right" in code_lower):
        tags.append("Tree")
    elif "linked list" in code_lower or "linkedlist" in code_lower:
        tags.append("Linked List")
    elif "stack" in code_lower:
        tags.append("Stack")
    elif "queue" in code_lower:
        tags.append("Queue")
    elif "heap" in code_lower or "priority queue" in code_lower:
        tags.append("Heap")
    
    # Language-specific patterns
    if language == "python" and ("dict" in code_lower or "hashmap" in code_lower):
        tags.append("Hash Table")
    elif language == "java" and ("hashmap" in code_lower or "hashtable" in code_lower):
        tags.append("Hash Table")
    elif language == "go" and "map[" in code_lower:
        tags.append("Hash Table")
    
    # Fallback tag
    if len(tags) <= 1:  # Only has the language tag
        tags.append("Algorithm")
    
    return tags

def create_solution_post(solution_info: Dict, explanation: Dict) -> None:
    """Create a Jekyll post file for the solution."""
    ensure_dir(OUTPUT_DIR)
    
    # Determine tags based on problem title and code
    tags = determine_tags(solution_info)
    
    # Create post content with front matter
    post = frontmatter.Post(
        explanation["explanation"],
        title=f"LeetCode {solution_info['problem_number']}: {solution_info['title']}",
        date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        slug=solution_info["problem_slug"],  # Add slug for permalink
        problem_number=solution_info["problem_number"],
        difficulty=solution_info["difficulty"],
        leetcode_url=solution_info["leetcode_url"],
        problem_statement=explanation["problem_statement"],
        approach=explanation["approach"],
        code=solution_info["code"],
        language=solution_info["language"],
        time_complexity=explanation["time_complexity"],
        space_complexity=explanation["space_complexity"],
        tags=tags,
    )
    
    # Create filename with date and problem slug
    date_prefix = datetime.now().strftime("%Y-%m-%d")
    filename = f"{date_prefix}-leetcode-{solution_info['problem_number']}-{solution_info['problem_slug']}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    # Write to file
    with open(filepath, "w") as f:
        f.write(frontmatter.dumps(post))
    
    print(f"Created solution post: {filepath}")

def process_solution_files() -> None:
    """Process changed solution files from git diff."""
    # Get changed solution files from environment variable (set by GitHub Actions)
    changed_files_str = os.environ.get("new_files", os.environ.get("new_py_files", ""))
    
    if not changed_files_str.strip():
        # If not in GitHub Actions, process all solution files for testing
        if not os.environ.get("GITHUB_ACTIONS"):
            changed_files = []
            for ext in [".py", ".java", ".go"]:
                changed_files.extend(glob.glob(f"{SOLUTIONS_DIR}/**/*{ext}", recursive=True))
        else:
            print("No changed solution files to process")
            return
    else:
        changed_files = changed_files_str.strip().split(" ")
    
    for file_path in changed_files:
        if not os.path.exists(file_path):
            print(f"File does not exist: {file_path}")
            continue
        
        # Only process Python, Java, and Go files
        if not file_path.endswith(('.py', '.java', '.go')):
            continue
            
        print(f"Processing: {file_path}")
        solution_info = extract_problem_info(file_path)
        
        if solution_info:
            try:
                explanation = generate_explanation(solution_info)
                create_solution_post(solution_info, explanation)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    ensure_dir(OUTPUT_DIR)
    process_solution_files()
