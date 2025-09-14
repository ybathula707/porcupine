import os
import json
import re
from pathlib import Path

FS_BASE_DIRECTORY=os.getenv("FS_BASE_DIRECTORY")
def repo_analyzer_simple(directory_path: str = FS_BASE_DIRECTORY) -> str:
    """
    Simplified repository analyzer that returns project information as a plain string report.
    
    Args:
        directory_path: Path to directory containing repositories to analyze
        
    Returns:
        String report with project details formatted as requested
    """
    
    def get_full_readme(repo_path: Path) -> str:
        """Extract the complete README content"""
        readme_patterns = ['README.md', 'README.rst', 'README.txt', 'README']
        for pattern in readme_patterns:
            readme_path = repo_path / pattern
            if readme_path.exists():
                try:
                    with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
                        return f.read().strip()
                except Exception:
                    continue
        return "No README found"

    def get_key_files(repo_path: Path) -> list:
        """Get list of key configuration and entry point files"""
        key_files = []
        important_files = {
            # Config files
            'requirements.txt', 'pyproject.toml', 'setup.py', 'Pipfile', 'poetry.lock',
            'package.json', 'package-lock.json', 'yarn.lock', 'tsconfig.json',
            'pom.xml', 'build.gradle', 'gradle.properties', 'build.xml',
            '.csproj', '.sln', 'packages.config',
            'go.mod', 'go.sum', 'Cargo.toml', 'Cargo.lock',
            'composer.json', 'composer.lock', 'Gemfile', 'Gemfile.lock',
            'CMakeLists.txt', 'Makefile', 'Dockerfile', '.gitignore',
            # Entry points
            'main.py', 'app.py', 'manage.py', 'run.py', '__init__.py',
            'index.js', 'main.js', 'app.js', 'server.js',
            'index.ts', 'main.ts', 'app.ts', 'server.ts',
            'Main.java', 'Application.java', 'App.java',
            'Program.cs', 'Main.cs', 'Startup.cs',
            'main.go', 'main.rs', 'index.php', 'main.php'
        }
        
        for item in repo_path.rglob('*'):
            if item.is_file() and (item.name in important_files or item.suffix == '.sln' or item.suffix.endswith('proj')):
                key_files.append(str(item.relative_to(repo_path)))
        
        return sorted(key_files)

    def parse_dependencies(repo_path: Path) -> list:
        """Parse common dependency files (requirements.txt and package.json only)"""
        deps = []
        
        # Python dependencies
        req_file = repo_path / 'requirements.txt'
        if req_file.exists():
            try:
                with open(req_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and not line.startswith('-'):
                            pkg = re.split(r'[<>=!]', line)[0].strip()
                            if pkg:
                                deps.append(pkg)
            except Exception:
                pass
        
        # JavaScript dependencies
        pkg_json = repo_path / 'package.json'
        if pkg_json.exists():
            try:
                with open(pkg_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for dep_type in ['dependencies', 'devDependencies']:
                    if dep_type in data:
                        deps.extend(data[dep_type].keys())
            except Exception:
                pass
        
        return sorted(list(set(deps)))

    def get_directories(repo_path: Path) -> list:
        """Get list of directories in the project"""
        dirs = [str(p.name) for p in repo_path.iterdir() if p.is_dir() and not p.name.startswith('.')]
        return sorted(dirs)

    # Main analysis logic
    base_path = Path(directory_path)
    if not base_path.exists():
        return f"Error: Directory {directory_path} does not exist"

    # Find repositories with code files
    potential_repos = []
    for item in base_path.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            has_project_files = any(
                f.suffix.lower() in ['.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.kt', '.cs', '.go', '.rs', '.php', '.rb', '.cpp', '.c']
                or f.name in ['package.json', 'pom.xml', 'requirements.txt', 'go.mod', 'Cargo.toml']
                for f in item.rglob('*') if f.is_file()
            )
            if has_project_files:
                potential_repos.append(item)

    # Generate reports for each repository
    reports = []
    for repo_path in potential_repos:
        name = repo_path.name
        readme = get_full_readme(repo_path)
        key_files = get_key_files(repo_path)
        dependencies = parse_dependencies(repo_path)
        directories = get_directories(repo_path)

        report_lines = [
            f"Name: {name}",
            f"README: {readme}",
            f"Key Files: {', '.join(key_files) if key_files else 'None'}",
            f"Dependencies: {', '.join(dependencies) if dependencies else 'None'}",
            f"Directories: {', '.join(directories) if directories else 'None'}",
            '=' * 80
        ]
        reports.append('\n'.join(report_lines))

    return '\n'.join(reports)


# Usage
if __name__ == "__main__":

    result = repo_analyzer_simple(FS_BASE_DIRECTORY)
    print(result)
