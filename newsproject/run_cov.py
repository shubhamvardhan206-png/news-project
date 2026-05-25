import subprocess
import sys
import os

os.chdir('C:\\Users\\SHUBHAM KUMAR\\Desktop\\news-project\\newsproject')

print("=" * 70)
print("Running Django Tests with Coverage")
print("=" * 70)

# Run coverage
cmd = [sys.executable, '-m', 'coverage', 'run', '--source=.', 'manage.py', 'test', 'news']
print(f"Executing: {' '.join(cmd)}\n")
result = subprocess.run(cmd)

if result.returncode == 0 or result.returncode is not None:
    print("\n" + "=" * 70)
    print("Coverage Report")
    print("=" * 70)
    subprocess.run([sys.executable, '-m', 'coverage', 'report'])
    
    print("\n" + "=" * 70)
    print("Generating HTML Report...")
    print("=" * 70)
    subprocess.run([sys.executable, '-m', 'coverage', 'html'])
    print("\n✓ HTML coverage report generated in: htmlcov/index.html")
