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
import traceback
from typing import Dict, List, Tuple, Optional

# Set up OpenAI client
openai.api_key = os.environ.get("OPENAI_API_KEY")
if not openai.api_key:
    print("Error: OPENAI_API_KEY environment variable not set")
    sys.exit(1)

# Configuration
SOLUTIONS_DIR = "problems"  # Root directory to scan for solutions
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
                model="gpt-3.5-turbo",  # Use the more widely available model
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
    """Determine tags based on the solution code, language, and directory structure."""
    tags = []
    code_lower = solution_info['code'].lower()
    language = solution_info['language']
    file_path = solution_info['file_path']
    
    # Add language tag
    tags.append(language.capitalize())
    
    # Add topic tag based on directory structure
    # Example: problems/two pointers/3sum.java -> tag: Two Pointers
    path_parts = file_path.split(os.sep)
    if len(path_parts) >= 2 and path_parts[0] == "problems":
        topic = path_parts[1]
        # Convert 'two pointers' to 'Two Pointers'
        topic_tag = ' '.join(word.capitalize() for word in topic.split())
        tags.append(topic_tag)
    
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
    """Create Jekyll post file and static HTML file for the solution."""
    # Ensure directories exist
    ensure_dir(OUTPUT_DIR)
    ensure_dir(f"solutions/{solution_info['problem_slug']}")
    
    # Determine tags based on problem title and code
    tags = determine_tags(solution_info)
    
    # Create post content with front matter for Jekyll
    post = frontmatter.Post(
        explanation["explanation"],
        title=f"LeetCode {solution_info['problem_number']}: {solution_info['title']}",
        date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        slug=solution_info["problem_slug"],  # Add slug for permalink
        permalink=f"/solutions/{solution_info['problem_slug']}/",  # Explicit permalink
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
    
    # Create filename with date and problem slug for Jekyll collection
    date_prefix = datetime.now().strftime("%Y-%m-%d")
    filename = f"{date_prefix}-leetcode-{solution_info['problem_number']}-{solution_info['problem_slug']}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    # Write Jekyll post file
    with open(filepath, "w") as f:
        f.write(frontmatter.dumps(post))
    
    print(f"Created Jekyll post: {filepath}")
    
    # Create static HTML file
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LeetCode #{solution_info['problem_number']}: {solution_info['title']}</title>
    <link rel="stylesheet" href="/leetcontentagent/assets/css/main.css">
    <link rel="stylesheet" href="/leetcontentagent/assets/css/syntax.css">
</head>
<body>
    <header class="site-header">
        <div class="container">
            <a class="site-title" href="/leetcontentagent/">Leetcode Solution Blog</a>
            <nav class="site-nav">
                <a href="/leetcontentagent/" class="nav-link">Home</a>
                <a href="/leetcontentagent/about/" class="nav-link">About</a>
                <a href="/leetcontentagent/archive/" class="nav-link">Archive</a>
            </nav>
        </div>
    </header>
    
    <main class="container">
        <article class="solution">
            <header class="solution-header">
                <h1 class="solution-title">LeetCode {solution_info['problem_number']}: {solution_info['title']}</h1>
                <div class="solution-meta">
                    <div class="problem-info">
                        <span class="difficulty {solution_info['difficulty'].lower()}">{solution_info['difficulty']}</span>
                        <span class="problem-number">#{solution_info['problem_number']}</span>
                        <a href="{solution_info['leetcode_url']}" class="leetcode-link" target="_blank">View on LeetCode</a>
                    </div>
                    
                    <div class="tags">
                        {" ".join([f'<span class="tag">{tag}</span>' for tag in tags])}
                    </div>
                </div>
            </header>

            <div class="problem-statement">
                <h2>Problem Statement</h2>
                {explanation['problem_statement']}
            </div>

            <div class="solution-approach">
                <h2>Approach</h2>
                {explanation['approach']}
            </div>

            <div class="solution-code">
                <h2>Code Solution ({solution_info['language'].capitalize()})</h2>
                <pre><code class="language-{solution_info['language']}">
{solution_info['code']}
                </code></pre>
            </div>

            <div class="solution-explanation">
                <h2>Explanation</h2>
                {explanation['explanation']}
            </div>

            <div class="solution-complexity">
                <h2>Complexity Analysis</h2>
                <p><strong>Time Complexity:</strong> {explanation['time_complexity']}</p>
                <p><strong>Space Complexity:</strong> {explanation['space_complexity']}</p>
            </div>
        </article>
    </main>
    
    <footer class="site-footer">
        <div class="container">
            <div class="footer-content">
                <p>&copy; {datetime.now().year} Leetcode Solution Blog</p>
                <p>A collection of detailed Leetcode solution explanations.</p>
            </div>
            <div class="footer-links">
                <a href="https://github.com/chirag-shinde/leetcontentagent" target="_blank">GitHub Repository</a>
            </div>
        </div>
    </footer>
</body>
</html>"""

    # Write static HTML file
    static_filepath = f"solutions/{solution_info['problem_slug']}/index.html"
    with open(static_filepath, "w") as f:
        f.write(html_content)
    
    print(f"Created static HTML: {static_filepath}")

def process_solution_files() -> None:
    """Process changed solution files from git diff."""
    print(f"OpenAI API Key present: {bool(openai.api_key)}")
    print(f"OpenAI API Key length: {len(openai.api_key) if openai.api_key else 0}")
    
    # Get changed solution files from environment variable (set by GitHub Actions)
    changed_files_str = os.environ.get("new_files", os.environ.get("new_py_files", ""))
    print(f"Changed files environment variable: '{changed_files_str}'")
    
    if not changed_files_str.strip():
        # If not in GitHub Actions, process all solution files for testing
        if not os.environ.get("GITHUB_ACTIONS"):
            changed_files = []
            for ext in [".py", ".java", ".go"]:
                pattern = f"{SOLUTIONS_DIR}/**/*{ext}"
                print(f"Searching for files with pattern: {pattern}")
                found_files = glob.glob(pattern, recursive=True)
                print(f"Found {len(found_files)} files: {found_files}")
                changed_files.extend(found_files)
        else:
            print("No changed solution files to process")
            return
    else:
        changed_files = changed_files_str.strip().split(" ")
        print(f"Processing changed files: {changed_files}")
    
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
                print(f"Generating explanation for {file_path}...")
                explanation = generate_explanation(solution_info)
                print(f"Successfully generated explanation, creating posts...")
                create_solution_post(solution_info, explanation)
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                print(f"Exception details: {traceback.format_exc()}")

if __name__ == "__main__":
    ensure_dir(OUTPUT_DIR)
    process_solution_files()
