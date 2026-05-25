#!/usr/bin/env python
import os
import subprocess
import sys

os.chdir('C:\\Users\\SHUBHAM KUMAR\\Desktop\\news-project\\newsproject')

print("=" * 70)
print("Running coverage tests...")
print("=" * 70)

# Run coverage
result = subprocess.run([sys.executable, '-m', 'coverage', 'run', '--source=.', 'manage.py', 'test'], 
                       capture_output=False)

print("\n" + "=" * 70)
print("Coverage Report:")
print("=" * 70)

# Generate text report
subprocess.run([sys.executable, '-m', 'coverage', 'report'])

print("\n" + "=" * 70)
print("Generating HTML Report...")
print("=" * 70)

# Generate HTML report
subprocess.run([sys.executable, '-m', 'coverage', 'html'])

print("\nHTML coverage report generated in: htmlcov/index.html")
