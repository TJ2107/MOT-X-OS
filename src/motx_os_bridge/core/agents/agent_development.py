"""
Agent Development - Agent spécialisé pour le développement et le code.
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import json
import re
import ast


@dataclass
class CodeAnalysis:
    """Représente une analyse de code."""
    file_path: str
    language: str
    lines_of_code: int
    functions: List[str]
    classes: List[str]
    imports: List[str]
    complexity: str
    issues: List[str]
    suggestions: List[str]


class AgentDevelopment:
    """Agent spécialisé pour le développement et le code."""
    
    def __init__(self):
        self.code_analyses: List[CodeAnalysis] = []
        self.project_structure: Dict[str, Any] = {}
        self.templates: Dict[str, str] = {}
        
        self._load_default_templates()
    
    def _load_default_templates(self):
        """Charge les templates de code par défaut."""
        self.templates = {
            "python_function": '''def {function_name}({parameters}):
    """
    {description}
    """
    {body}
''',
            "python_class": '''class {class_name}:
    """
    {description}
    """
    
    def __init__(self{init_params}):
        {init_body}
    
    {methods}
''',
            "python_script": '''#!/usr/bin/env python3
"""
{description}
"""

import sys
from pathlib import Path


def main():
    """Point d'entrée principal."""
    {main_body}


if __name__ == "__main__":
    main()
''',
            "powershell_script": '''# {description}
# Author: MOT-X OS

param(
    [Parameter(Mandatory=$true)]
    [string]${param_name}
)

{body}
'''
        }
    
    async def analyze_code(self, file_path: str) -> CodeAnalysis:
        """Analyse un fichier de code."""
        try:
            path = Path(file_path)
            if not path.exists():
                raise Exception(f"Fichier non trouvé: {file_path}")
            
            content = path.read_text(encoding='utf-8')
            language = self._detect_language(file_path)
            
            analysis = CodeAnalysis(
                file_path=file_path,
                language=language,
                lines_of_code=len(content.splitlines()),
                functions=[],
                classes=[],
                imports=[],
                complexity="unknown",
                issues=[],
                suggestions=[]
            )
            
            if language == "python":
                await self._analyze_python(content, analysis)
            elif language == "powershell":
                await self._analyze_powershell(content, analysis)
            elif language == "javascript":
                await self._analyze_javascript(content, analysis)
            
            # Détection de problèmes
            analysis.issues = await self._detect_issues(content, language)
            
            # Suggestions d'amélioration
            analysis.suggestions = await self._generate_suggestions(analysis)
            
            self.code_analyses.append(analysis)
            
            return analysis
            
        except Exception as e:
            raise Exception(f"Erreur analyse code: {str(e)}")
    
    def _detect_language(self, file_path: str) -> str:
        """Détecte le langage du fichier."""
        ext = Path(file_path).suffix.lower()
        
        extensions = {
            ".py": "python",
            ".ps1": "powershell",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".go": "go",
            ".rs": "rust",
            ".rb": "ruby"
        }
        
        return extensions.get(ext, "unknown")
    
    async def _analyze_python(self, content: str, analysis: CodeAnalysis):
        """Analyse du code Python."""
        try:
            tree = ast.parse(content)
            
            # Extraction des fonctions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis.functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    analysis.classes.append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis.imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    analysis.imports.append(f"from {node.module}")
            
            # Estimation de la complexité
            analysis.complexity = self._estimate_complexity(analysis.lines_of_code, len(analysis.functions))
            
        except SyntaxError:
            analysis.issues.append("Erreur de syntaxe Python détectée")
    
    async def _analyze_powershell(self, content: str, analysis: CodeAnalysis):
        """Analyse du code PowerShell."""
        # Extraction des fonctions
        functions = re.findall(r'function\s+(\w+)', content)
        analysis.functions = functions
        
        # Estimation de la complexité
        analysis.complexity = self._estimate_complexity(analysis.lines_of_code, len(functions))
    
    async def _analyze_javascript(self, content: str, analysis: CodeAnalysis):
        """Analyse du code JavaScript."""
        # Extraction des fonctions
        functions = re.findall(r'function\s+(\w+)|(\w+)\s*=\s*function', content)
        analysis.functions = [f[0] or f[1] for f in functions if f[0] or f[1]]
        
        # Estimation de la complexité
        analysis.complexity = self._estimate_complexity(analysis.lines_of_code, len(analysis.functions))
    
    def _estimate_complexity(self, lines: int, functions: int) -> str:
        """Estime la complexité du code."""
        if lines < 50:
            return "simple"
        elif lines < 200:
            return "moderate"
        elif lines < 500:
            return "complex"
        else:
            return "very_complex"
    
    async def _detect_issues(self, content: str, language: str) -> List[str]:
        """Détecte les problèmes dans le code."""
        issues = []
        
        # Problèmes génériques
        if "TODO" in content or "FIXME" in content:
            issues.append("Présence de TODO/FIXME dans le code")
        
        if "print(" in content and language == "python":
            issues.append("Utilisation de print() pour le débogage")
        
        if content.count("except:") > 0:
            issues.append("Exceptions catchées sans spécification")
        
        # Problèmes spécifiques au langage
        if language == "python":
            if "import *" in content:
                issues.append("Import wildcard détecté")
            
            if not re.search(r'""".*"""', content, re.DOTALL):
                issues.append("Absence de docstring détectée")
        
        return issues
    
    async def _generate_suggestions(self, analysis: CodeAnalysis) -> List[str]:
        """Génère des suggestions d'amélioration."""
        suggestions = []
        
        if analysis.complexity in ["complex", "very_complex"]:
            suggestions.append("Considérer la refactorisation en modules plus petits")
        
        if len(analysis.functions) > 20:
            suggestions.append("Trop de fonctions - envisager la séparation en classes")
        
        if not analysis.imports and analysis.language == "python":
            suggestions.append("Considérer l'ajout de docstrings pour la documentation")
        
        if not suggestions:
            suggestions.append("Code semble bien structuré")
        
        return suggestions
    
    async def generate_code(self, template_name: str, **kwargs) -> str:
        """Génère du code à partir d'un template."""
        if template_name not in self.templates:
            raise Exception(f"Template non trouvé: {template_name}")
        
        template = self.templates[template_name]
        
        try:
            code = template.format(**kwargs)
            return code
        except KeyError as e:
            raise Exception(f"Paramètre manquant pour le template: {str(e)}")
    
    async def refactor_code(self, code: str, refactor_type: str = "cleanup") -> str:
        """Refactorise du code."""
        if refactor_type == "cleanup":
            # Nettoyage basique
            lines = code.split('\n')
            cleaned = [line.rstrip() for line in lines if line.strip() or line == '\n']
            return '\n'.join(cleaned)
        
        elif refactor_type == "format":
            # Formatage basique
            lines = code.split('\n')
            formatted = []
            indent_level = 0
            
            for line in lines:
                stripped = line.strip()
                if stripped.endswith(':'):
                    formatted.append('    ' * indent_level + stripped)
                    indent_level += 1
                elif stripped and not stripped.startswith('#'):
                    if stripped in ('else', 'elif', 'except', 'finally'):
                        indent_level -= 1
                    formatted.append('    ' * indent_level + stripped)
                else:
                    formatted.append('    ' * indent_level + stripped)
            
            return '\n'.join(formatted)
        
        return code
    
    async def analyze_project(self, project_path: str) -> Dict[str, Any]:
        """Analyse la structure d'un projet."""
        try:
            path = Path(project_path)
            if not path.exists():
                raise Exception(f"Projet non trouvé: {project_path}")
            
            structure = {
                "path": project_path,
                "files": [],
                "directories": [],
                "languages": {},
                "total_files": 0,
                "total_lines": 0
            }
            
            for item in path.rglob("*"):
                if item.is_file():
                    structure["files"].append(str(item))
                    structure["total_files"] += 1
                    
                    # Comptage des lignes
                    try:
                        lines = len(item.read_text(encoding='utf-8').splitlines())
                        structure["total_lines"] += lines
                    except:
                        pass
                    
                    # Détection du langage
                    lang = self._detect_language(str(item))
                    if lang != "unknown":
                        structure["languages"][lang] = structure["languages"].get(lang, 0) + 1
                
                elif item.is_dir():
                    structure["directories"].append(str(item))
            
            self.project_structure = structure
            return structure
            
        except Exception as e:
            raise Exception(f"Erreur analyse projet: {str(e)}")
    
    async def run_tests(self, project_path: str) -> Dict[str, Any]:
        """Exécute les tests d'un projet."""
        try:
            import subprocess
            
            # Détection du framework de test
            if (Path(project_path) / "pytest.ini").exists() or (Path(project_path) / "pyproject.toml").exists():
                # pytest
                result = subprocess.run(
                    ["pytest", "-v"],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                return {
                    "framework": "pytest",
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            
            elif (Path(project_path) / "package.json").exists():
                # npm/jest
                result = subprocess.run(
                    ["npm", "test"],
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                return {
                    "framework": "npm",
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            
            else:
                return {
                    "framework": "unknown",
                    "error": "Aucun framework de test détecté"
                }
            
        except Exception as e:
            raise Exception(f"Erreur exécution tests: {str(e)}")
    
    async def create_project_structure(self, project_name: str, project_type: str = "python") -> Dict[str, Any]:
        """Crée la structure d'un nouveau projet."""
        try:
            base_path = Path(project_name)
            base_path.mkdir(exist_ok=True)
            
            structure = {
                "name": project_name,
                "type": project_type,
                "created_files": []
            }
            
            if project_type == "python":
                # Structure Python
                (base_path / "src").mkdir(exist_ok=True)
                (base_path / "tests").mkdir(exist_ok=True)
                (base_path / "docs").mkdir(exist_ok=True)
                
                # Fichiers de base
                (base_path / "README.md").write_text(f"# {project_name}\n")
                (base_path / "requirements.txt").write_text("")
                (base_path / ".gitignore").write_text("*.pyc\n__pycache__/\n")
                
                structure["created_files"] = ["src/", "tests/", "docs/", "README.md", "requirements.txt", ".gitignore"]
            
            elif project_type == "javascript":
                # Structure JavaScript
                (base_path / "src").mkdir(exist_ok=True)
                (base_path / "tests").mkdir(exist_ok=True)
                (base_path / "dist").mkdir(exist_ok=True)
                
                (base_path / "package.json").write_text(json.dumps({
                    "name": project_name,
                    "version": "1.0.0",
                    "main": "src/index.js"
                }, indent=2))
                
                structure["created_files"] = ["src/", "tests/", "dist/", "package.json"]
            
            return structure
            
        except Exception as e:
            raise Exception(f"Erreur création projet: {str(e)}")
    
    def get_code_analyses(self) -> List[CodeAnalysis]:
        """Retourne les analyses de code."""
        return self.code_analyses
    
    def clear_analyses(self):
        """Efface les analyses de code."""
        self.code_analyses.clear()
