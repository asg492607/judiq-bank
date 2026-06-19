const fs = require('fs');
const path = require('path');

const scriptPath = path.join(__dirname, '..', 'frontend', 'script.js');
let content = fs.readFileSync(scriptPath, 'utf8');

// A simple regex approach to find `.innerHTML = ` and replace the right hand side
// with DOMPurify.sanitize(RHS)
// Because RHS could span multiple lines, we will do a more robust string manipulation.

// Let's just find lines with `.innerHTML = ` and check if they are already sanitized.
const lines = content.split('\n');
let modifiedCount = 0;

for (let i = 0; i < lines.length; i++) {
    let line = lines[i];
    if (line.includes('.innerHTML =') && !line.includes('DOMPurify.sanitize') && !line.includes('JudiQ_UI.sanitize')) {
        // Find the index of `= `
        const eqIdx = line.indexOf('= ');
        if (eqIdx !== -1) {
            const prefix = line.substring(0, eqIdx + 2);
            let suffix = line.substring(eqIdx + 2);
            
            // If the suffix ends with `;`, we wrap the inside.
            // If it's a template literal that spans multiple lines, we need to trace it.
            // Let's print out what we found first.
            console.log(`Found on line ${i+1}: ${line.trim()}`);
        }
    }
}
