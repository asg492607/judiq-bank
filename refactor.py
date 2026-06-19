import re

with open('backend/session.py', 'r') as f:
    lines = f.readlines()

new_lines = []
in_conn_block = False
indent_amount = 0

for i, line in enumerate(lines):
    if line.startswith('import '):
        if 'contextlib' not in ''.join(lines):
            lines.insert(0, 'from contextlib import closing\n')
            break
            
with open('backend/session.py', 'w') as f:
    f.writelines(lines)

with open('backend/session.py', 'r') as f:
    content = f.read()

# Let's replace conn = DatabaseManager.get_connection() with with closing(DatabaseManager.get_connection()) as conn:
# And we also need to indent everything until the except Exception as e: block.
# This is tricky using regex.
