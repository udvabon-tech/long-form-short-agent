#!/usr/bin/env python3
"""
Installation verification script for Long Form to Shorts v3.0
"""

import sys
import os
from pathlib import Path


def check_python_version():
    """Verify Python version is 3.8+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        return False, f"Python {version.major}.{version.minor} (need 3.8+)"
    return True, f"Python {version.major}.{version.minor}.{version.micro}"


def check_dependencies():
    """Check if required Python packages are installed"""
    results = {}

    try:
        import yaml
        results['pyyaml'] = (True, yaml.__version__)
    except ImportError:
        results['pyyaml'] = (False, "Not installed")

    try:
        import google.generativeai as genai
        # Try to get version
        try:
            version = genai.__version__
        except:
            version = "installed"
        results['google-generativeai'] = (True, version)
    except ImportError:
        results['google-generativeai'] = (False, "Not installed")

    return results


def check_ffmpeg():
    """Verify FFmpeg is installed with libass support"""
    import subprocess

    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            return False, "FFmpeg command failed"

        output = result.stdout
        version_line = output.splitlines()[0] if output else "Unknown version"
        has_libass = "--enable-libass" in output

        if not has_libass:
            return False, f"{version_line} (missing libass)"

        return True, version_line

    except FileNotFoundError:
        return False, "FFmpeg not found in PATH"
    except Exception as e:
        return False, f"Error checking FFmpeg: {str(e)}"


def check_api_key():
    """Check if GEMINI_API_KEY is set"""
    key = os.environ.get('GEMINI_API_KEY')
    if not key:
        return False, "Not set"
    if len(key) < 20:
        return False, "Seems too short"
    # Mask most of the key
    masked = key[:8] + "..." + key[-4:]
    return True, f"Set ({masked})"


def check_file_structure():
    """Verify required files and directories exist"""
    required_files = [
        'config.yaml',
        'requirements-new.txt',
        'src/__init__.py',
        'src/agents/orchestrator.py',
        'src/config/settings.py',
        'src/utils/logging.py',
    ]

    required_dirs = [
        'src/agents',
        'src/config',
        'src/utils',
        'Scripts',
        'Projects',
        'Templates',
    ]

    results = {'files': {}, 'dirs': {}}

    for file_path in required_files:
        path = Path(file_path)
        results['files'][file_path] = path.exists()

    for dir_path in required_dirs:
        path = Path(dir_path)
        results['dirs'][dir_path] = path.exists() and path.is_dir()

    return results


def check_config_file():
    """Verify config.yaml is valid"""
    try:
        import yaml
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)

        required_sections = ['system', 'api', 'video', 'subtitle', 'error_handling']
        missing = [s for s in required_sections if s not in config]

        if missing:
            return False, f"Missing sections: {', '.join(missing)}"

        return True, "Valid YAML with all required sections"

    except FileNotFoundError:
        return False, "config.yaml not found"
    except yaml.YAMLError as e:
        return False, f"YAML syntax error: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def print_header(text):
    """Print a formatted header"""
    print(f"\n{'=' * 70}")
    print(f"  {text}")
    print(f"{'=' * 70}")


def print_check(name, status, details):
    """Print a check result"""
    icon = "✓" if status else "✗"
    color = "\033[92m" if status else "\033[91m"  # Green or Red
    reset = "\033[0m"
    print(f"{color}{icon}{reset} {name:40s} {details}")


def main():
    """Run all verification checks"""
    print_header("Long Form to Shorts v3.0 - Installation Verification")

    all_passed = True

    # Python version
    print_header("Python Environment")
    status, details = check_python_version()
    print_check("Python Version", status, details)
    if not status:
        all_passed = False

    # Dependencies
    print_header("Python Dependencies")
    deps = check_dependencies()
    for name, (status, details) in deps.items():
        print_check(name, status, details)
        if not status:
            all_passed = False

    # FFmpeg
    print_header("External Tools")
    status, details = check_ffmpeg()
    print_check("FFmpeg (with libass)", status, details)
    if not status:
        all_passed = False

    # API Key
    status, details = check_api_key()
    print_check("GEMINI_API_KEY", status, details)
    if not status:
        all_passed = False

    # File structure
    print_header("File Structure")
    structure = check_file_structure()

    files_ok = all(structure['files'].values())
    dirs_ok = all(structure['dirs'].values())

    print_check("Required Files", files_ok, f"{sum(structure['files'].values())}/{len(structure['files'])} found")
    print_check("Required Directories", dirs_ok, f"{sum(structure['dirs'].values())}/{len(structure['dirs'])} found")

    if not files_ok or not dirs_ok:
        all_passed = False
        print("\nMissing items:")
        for path, exists in structure['files'].items():
            if not exists:
                print(f"  ✗ File: {path}")
        for path, exists in structure['dirs'].items():
            if not exists:
                print(f"  ✗ Directory: {path}")

    # Configuration file
    print_header("Configuration")
    status, details = check_config_file()
    print_check("config.yaml", status, details)
    if not status:
        all_passed = False

    # Final summary
    print_header("Summary")
    if all_passed:
        print("\n✓ All checks passed! Your installation is ready.")
        print("\nNext steps:")
        print("  1. Read START_HERE_V3.md for quick start")
        print("  2. Test the system with a sample video")
        print("  3. Review config.yaml settings")
        print("\nTo test the orchestrator:")
        print("  python -c \"from src.agents.orchestrator import create_orchestrator; print('OK')\"")
        return 0
    else:
        print("\n✗ Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  • Python packages: pip install -r requirements-new.txt")
        print("  • FFmpeg: brew install ffmpeg (macOS) or sudo apt install ffmpeg (Linux)")
        print("  • API Key: export GEMINI_API_KEY='your-key-here'")
        print("  • Missing files: Re-download or restore from backup")
        return 1


if __name__ == "__main__":
    sys.exit(main())
