// generate.js
// Wrapper called by `npm run generate -- "checkout process"`
// Derives the output filename from the query and calls the Python CLI.

const { execSync } = require('child_process');

const query = process.argv[2];

if (!query) {
  console.error('Usage: npm run generate -- "<query>"');
  console.error('Example: npm run generate -- "checkout process"');
  process.exit(1);
}

// "checkout process" → "checkout_process.spec.ts"
const filename = query.trim().toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '') + '.spec.ts';
const outPath = `generated_tests/${filename}`;

const cmd = `python -m playwright_rag.cli generate "${query}" --docs docs/ --out ${outPath}`;

console.log(`Query   : ${query}`);
console.log(`Output  : ${outPath}`);
console.log(`Running : ${cmd}\n`);

execSync(cmd, { stdio: 'inherit' });
