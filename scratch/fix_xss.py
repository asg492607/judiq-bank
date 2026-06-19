import re
import os

script_path = r"c:\Users\Atharva\OneDrive\Desktop\Level_0judiq\frontend\script.js"

with open(script_path, "r", encoding="utf-8") as f:
    content = f.read()

# We want to replace something like:
# foo.innerHTML = `bar`
# with:
# foo.innerHTML = DOMPurify.sanitize(`bar`)
# But it can be multi-line.
# Actually, since it's hard to regex match arbitrary multi-line JS expressions,
# it might be easier to use a simple string replacement for known patterns or do it manually for the major ones.

# Let's count how many .innerHTML we have
count = content.count(".innerHTML =")
print(f"Found {count} instances of .innerHTML =")

# Let's find them and print them to see the structure
matches = re.finditer(r'([a-zA-Z0-9_]+)\.innerHTML\s*=\s*(.*?);', content, re.DOTALL)
for i, m in enumerate(matches):
    if i < 5:
        print(f"Match {i}: {m.group(1)}.innerHTML = {m.group(2)[:50]}...")
