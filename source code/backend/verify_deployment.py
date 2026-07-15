#!/usr/bin/env python3
"""
Deployment Verification Script
Ensures system is ready for production use
"""

import os
import sys
import json
import subprocess
from pathlib import Path


class DeploymentChecker:
    """Verify deployment readiness"""
    
    def __init__(self):
        self.checks = []
        self.errors = []
        self.warnings = []
    
    def check(self, name: str, condition: bool, message: str = ""):
        """Record a check result"""
        status = "✓" if condition else "✗"
        self.checks.append((status, name, message))
        if not condition:
            self.errors.append(f"{name}: {message}")
    
    def warn(self, message: str):
        """Record a warning"""
        self.warnings.append(message)
    
    def print_report(self):
        """Print verification report"""
        print("\n" + "=" * 70)
        print("DEPLOYMENT VERIFICATION REPORT")
        print("=" * 70 + "\n")
        
        # Print checks
        for status, name, message in self.checks:
            print(f"{status} {name}")
            if message:
                print(f"  {message}")
        
        # Summary
        print("\n" + "-" * 70)
        passed = sum(1 for s, _, _ in self.checks if s == "✓")
        total = len(self.checks)
        print(f"Results: {passed}/{total} checks passed")
        
        # Warnings
        if self.warnings:
            print("\nWarnings:")
            for w in self.warnings:
                print(f"  ⚠ {w}")
        
        # Errors
        if self.errors:
            print("\nErrors:")
            for e in self.errors:
                print(f"  ✗ {e}")
        
        print("=" * 70 + "\n")
        
        return len(self.errors) == 0
    
    def verify_all(self):
        """Run all verification checks"""
        self.verify_structure()
        self.verify_dependencies()
        self.verify_configuration()
        self.verify_services()
        self.verify_performance()
    
    def verify_structure(self):
        """Verify directory and file structure"""
        print("Checking directory structure...")
        
        # Required directories
        dirs = ["recordings", "transcripts", "moms", "models"]
        for d in dirs:
            exists = os.path.isdir(d)
            self.check(f"Directory: {d}", exists, f"Created: {exists}")
        
        # Required files
        files = {
            "main.exe": "Whisper executable",
            "whisper.dll": "Whisper library",
            "config.json": "Configuration file",
            "mom_generator.py": "Main script",
            "setup.py": "Setup script"
        }
        
        for filename, desc in files.items():
            exists = os.path.isfile(filename)
            self.check(f"File: {filename}", exists, desc)
        
        # Model file
        model_exists = os.path.isfile("models/ggml-medium.bin")
        self.check("Model: ggml-medium.bin", model_exists, "Whisper model")
    
    def verify_dependencies(self):
        """Verify Python dependencies"""
        print("Checking Python dependencies...")
        
        try:
            import requests
            self.check("Module: requests", True, "Required for HTTP calls")
        except ImportError:
            self.check("Module: requests", False, "Install: pip install requests")
        
        # Python version
        version = sys.version_info
        python_ok = version.major == 3 and version.minor >= 7
        self.check(
            f"Python {version.major}.{version.minor}",
            python_ok,
            "Required: 3.7 or higher"
        )
    
    def verify_configuration(self):
        """Verify configuration"""
        print("Checking configuration...")
        
        config_exists = os.path.isfile("config.json")
        self.check("Config file exists", config_exists)
        
        if config_exists:
            try:
                with open("config.json", 'r') as f:
                    config = json.load(f)
                
                self.check("Config JSON valid", True)
                
                # Check required keys
                required = ["whisper_exe", "whisper_model", "ollama_url", "ollama_model"]
                for key in required:
                    exists = key in config
                    self.check(f"Config key: {key}", exists)
                
                # Check file references
                if "whisper_exe" in config:
                    exe_exists = os.path.isfile(config["whisper_exe"])
                    self.check(
                        f"Whisper executable",
                        exe_exists,
                        config["whisper_exe"]
                    )
                
                if "whisper_model" in config:
                    model_exists = os.path.isfile(config["whisper_model"])
                    self.check(
                        f"Whisper model",
                        model_exists,
                        config["whisper_model"]
                    )
            
            except json.JSONDecodeError as e:
                self.check("Config JSON valid", False, f"JSON error: {str(e)}")
    
    def verify_services(self):
        """Verify external services"""
        print("Checking external services...")
        
        # Ollama server
        try:
            import requests
            response = requests.get(
                "http://localhost:11434/api/tags",
                timeout=5
            )
            
            if response.status_code == 200:
                models = response.json().get('models', [])
                self.check(
                    "Ollama server running",
                    True,
                    f"Found {len(models)} model(s)"
                )
                
                if not models:
                    self.warn("No models on ollama server. Run: ollama pull llama2")
                
                model_names = [m['name'] for m in models]
                self.check(
                    "Models available",
                    len(model_names) > 0,
                    ", ".join(model_names[:3])
                )
            else:
                self.check("Ollama server", False, f"HTTP {response.status_code}")
        
        except requests.exceptions.ConnectionError:
            self.check(
                "Ollama server running",
                False,
                "Start with: ollama serve"
            )
        except Exception as e:
            self.check("Ollama connection", False, str(e))
    
    def verify_performance(self):
        """Verify system performance"""
        print("Checking system performance...")
        
        # Disk space
        try:
            import shutil
            total, used, free = shutil.disk_usage("/")
            free_gb = free / (1024**3)
            
            adequate = free_gb > 1  # At least 1GB free
            self.check(
                f"Disk space",
                adequate,
                f"{free_gb:.1f}GB free (recommended: >1GB)"
            )
        except:
            self.warn("Could not check disk space")
        
        # Memory
        try:
            import psutil
            memory = psutil.virtual_memory()
            available_gb = memory.available / (1024**3)
            
            adequate = available_gb > 2  # At least 2GB available
            self.check(
                f"Memory available",
                adequate,
                f"{available_gb:.1f}GB available (recommended: >4GB)"
            )
        except ImportError:
            self.warn("psutil not installed, skipping memory check")
        except:
            self.warn("Could not check memory")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Verify deployment readiness"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Attempt to fix common issues"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed output"
    )
    
    args = parser.parse_args()
    
    checker = DeploymentChecker()
    checker.verify_all()
    success = checker.print_report()
    
    if args.fix and not success:
        print("\nAttempting to fix common issues...")
        
        # Create directories
        for d in ["recordings", "transcripts", "moms"]:
            os.makedirs(d, exist_ok=True)
            print(f"✓ Created directory: {d}")
        
        # Install dependencies
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-q", "requests"
            ])
            print("✓ Installed required dependencies")
        except:
            print("✗ Failed to install dependencies")
        
        # Re-verify
        print("\nRe-verifying after fixes...")
        checker2 = DeploymentChecker()
        checker2.verify_all()
        checker2.print_report()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
