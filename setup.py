"""
Setup and Configuration Script for MOM Generator
Handles environment setup and verification
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_success(text):
    """Print success message"""
    print(f"✓ {text}")


def print_error(text):
    """Print error message"""
    print(f"✗ {text}")


def print_info(text):
    """Print info message"""
    print(f"ℹ {text}")


def check_python():
    """Check Python installation"""
    print_header("Checking Python Installation")
    
    version = sys.version_info
    python_version = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print_error(f"Python 3.7+ required, found {python_version}")
        return False
    
    print_success(f"Python {python_version} found")
    print_info(f"Python executable: {sys.executable}")
    return True


def install_dependencies():
    """Install required Python packages"""
    print_header("Installing Dependencies")
    
    try:
        print_info("Installing required packages...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"
        ])
        print_success("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print_error("Failed to install dependencies")
        print_info("Try running manually: python -m pip install -r requirements.txt")
        return False


def check_whisper_setup():
    """Check whisper.cpp setup"""
    print_header("Checking Whisper.cpp Setup")
    
    checks = {
        "main.exe": "Whisper executable",
        "models/ggml-medium.bin": "Whisper model"
    }
    
    all_good = True
    for file, description in checks.items():
        if os.path.exists(file):
            size = os.path.getsize(file)
            print_success(f"{description}: {file} ({size:,} bytes)")
        else:
            print_error(f"{description} not found: {file}")
            all_good = False
    
    return all_good


def check_ollama():
    """Check ollama server connection"""
    print_header("Checking Ollama Server")
    
    try:
        import requests
        
        print_info("Connecting to http://localhost:11434...")
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        
        if response.status_code == 200:
            models = response.json().get('models', [])
            print_success(f"Ollama server is running")
            
            if models:
                print_success(f"Found {len(models)} model(s):")
                for model in models:
                    name = model.get('name', 'unknown')
                    size = model.get('size', 0)
                    print_info(f"  - {name} ({size:,} bytes)")
            else:
                print_error("No models found on ollama server")
                print_info("Run: ollama pull llama2")
                return False
            
            return True
        else:
            print_error(f"Ollama responded with status {response.status_code}")
            return False
    
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to ollama server")
        print_info("Make sure ollama is running: ollama serve")
        return False
    except Exception as e:
        print_error(f"Error checking ollama: {str(e)}")
        return False


def create_directories():
    """Create necessary directories"""
    print_header("Creating Directory Structure")
    
    directories = [
        "recordings",
        "transcripts",
        "moms",
        "models"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print_success(f"Directory ready: {directory}")


def validate_config():
    """Validate configuration file"""
    print_header("Validating Configuration")
    
    if not os.path.exists("config.json"):
        print_error("config.json not found")
        return False
    
    try:
        with open("config.json", 'r') as f:
            config = json.load(f)
        
        required_keys = [
            "whisper_exe",
            "whisper_model",
            "ollama_url",
            "ollama_model",
            "output_dir"
        ]
        
        missing = [k for k in required_keys if k not in config]
        if missing:
            print_error(f"Missing config keys: {', '.join(missing)}")
            return False
        
        print_success("config.json is valid")
        print_info(f"Ollama URL: {config['ollama_url']}")
        print_info(f"Ollama Model: {config['ollama_model']}")
        print_info(f"Whisper Model: {config['whisper_model']}")
        
        return True
    
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON in config.json: {str(e)}")
        return False
    except Exception as e:
        print_error(f"Error reading config.json: {str(e)}")
        return False


def run_full_setup():
    """Run complete setup"""
    print_header("MOM Generator - Full Setup")
    
    results = {
        "Python": check_python(),
        "Whisper Setup": check_whisper_setup(),
        "Configuration": validate_config(),
        "Dependencies": install_dependencies(),
        "Ollama Connection": check_ollama(),
    }
    
    create_directories()
    
    # Summary
    print_header("Setup Summary")
    
    all_passed = all(results.values())
    for check, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {check}")
    
    print()
    
    if all_passed:
        print_success("All checks passed! Ready to use MOM Generator")
        print_info("Next steps:")
        print_info("  1. Place audio files in 'recordings' directory")
        print_info("  2. Run: generate_mom_batch.bat recordings")
        print_info("  3. Check 'moms' directory for output")
        return True
    else:
        print_error("Some checks failed. Please review above.")
        print_info("For help, see README.md")
        return False


def quick_test():
    """Quick environment test"""
    print_header("Quick Environment Test")
    
    checks_passed = 0
    checks_total = 0
    
    # Test Python
    checks_total += 1
    if check_python():
        checks_passed += 1
    
    # Test Whisper
    checks_total += 1
    if check_whisper_setup():
        checks_passed += 1
    
    # Test Config
    checks_total += 1
    if validate_config():
        checks_passed += 1
    
    # Test Ollama
    checks_total += 1
    if check_ollama():
        checks_passed += 1
    
    print()
    print(f"Results: {checks_passed}/{checks_total} checks passed")
    return checks_passed == checks_total


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Setup MOM Generator environment"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick environment test only"
    )
    
    args = parser.parse_args()
    
    if args.quick:
        success = quick_test()
    else:
        success = run_full_setup()
    
    sys.exit(0 if success else 1)
