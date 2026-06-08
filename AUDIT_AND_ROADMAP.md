extensions = ["*.py"]
ignore = [
    "*/__pycache__/*",
    "*/tests/*",
    "*.egg-info/*",
    "*.egg",
    "dist/*",
    "build/*",
]

lint = ["ruff", "--fix", "extensions"]
