import sys
import io
# Force UTF-8 encoding for stdout/stderr on Ubuntu
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Set default encoding
import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
from app import create_app
app = create_app()

if __name__ == '__main__':
    app.run()
