import os
import sys
import django
from coverage import Coverage

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newsproject.settings')
sys.path.insert(0, 'C:\\Users\\SHUBHAM KUMAR\\Desktop\\news-project\\newsproject')

django.setup()

# Initialize and start coverage
cov = Coverage(source=['.'])
cov.start()

# Run tests
from django.test.utils import get_runner
from django.conf import settings

TestRunner = get_runner(settings)
test_runner = TestRunner(verbosity=2, interactive=True, keepdb=False)

print("=" * 70)
print("Running tests with coverage...")
print("=" * 70)

failures = test_runner.run_tests(['news'])

# Stop coverage and generate reports
cov.stop()
cov.save()

print("\n" + "=" * 70)
print("Coverage Report")
print("=" * 70)
cov.report()

# Generate HTML report
print("\n" + "=" * 70)
print("Generating HTML coverage report...")
print("=" * 70)
cov.html_report(directory='htmlcov')
print("HTML report saved to: htmlcov/index.html")

sys.exit(bool(failures))
