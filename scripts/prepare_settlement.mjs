import ts from 'typescript';
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import vm from 'node:vm';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const [sourcePath, outputPath] = process.argv.slice(2);
const hash = value => createHash('sha256').update(value).digest('hex');
const fail = message => { throw new Error(message); };
const pin = JSON.parse(readFileSync(resolve(root, 'experiments/gillian-settlement/source-pin.json')));
const raw = readFileSync(sourcePath);
if (hash(raw) !== pin.sha256) fail('Source pin mismatch');
if (ts.version !== '5.9.3') fail('Wrong TypeScript version');
const source = raw.toString('utf8');
const file = ts.createSourceFile(pin.path, source, ts.ScriptTarget.ES2022, true, ts.ScriptKind.TS);
if (file.parseDiagnostics.length) fail('Source parse diagnostics');
const functions = file.statements.filter(node => ts.isFunctionDeclaration(node) && node.name?.text === pin.function);
if (functions.length !== 1) fail('Function selection mismatch');
const declaration = raw.subarray(pin.declarationByteSpan.start, pin.declarationByteSpan.end).toString('utf8');
if (declaration !== functions[0].getText(file) || !declaration.startsWith('export function ')) fail('Independent span mismatch');
const base = declaration.slice('export '.length);
const variants = {
  base,
  'wrong-comparison': base.replace('outcome.actual === intent.local', 'outcome.actual !== intent.local'),
  'unconditional-promotion': base.replace('return outcome;', 'return { kind: \"committed\", version: intent.local };'),
  'wrong-version': base.replace('version: outcome.actual', 'version: "WRONG_VERSION"'),
  'equivalent-null-check': base.replace('outcome.actual !== null && ', ''),
  'equivalent-layout': base.replace('  if (', '  /* harmless layout */\n    if (').replace('return outcome;', 'return   outcome;'),
};
function emit(text) {
  const result = ts.transpileModule(text, { compilerOptions: { target: ts.ScriptTarget.ES5, module: ts.ModuleKind.CommonJS,
    removeComments: true, alwaysStrict: true }, reportDiagnostics: true });
  if (result.diagnostics?.some(d => d.category === ts.DiagnosticCategory.Error)) fail('Type erasure diagnostics: ' + result.diagnostics.map(d => ts.flattenDiagnosticMessageText(d.messageText, ' ')).join('; '));
  return result.outputText;
}
mkdirSync(outputPath, { recursive: true });
const receipt = { pin, parser: ts.version, node: process.version, variants: {} };
for (const [name, text] of Object.entries(variants)) {
  if (name !== 'base' && text === base) fail('Mutation did not change source: ' + name);
  const emitted = emit(text);
  const directory = resolve(outputPath, name);
  mkdirSync(directory, { recursive: true });
  writeFileSync(resolve(directory, 'source.ts'), text + '\n');
  writeFileSync(resolve(directory, 'subject.js'), emitted);
  const sandbox = {};
  vm.runInNewContext(emitted + '\nthis.subject = settleAgainstIntent;', sandbox, { timeout: 1000 });
  const fixtures = [];
  for (const local of ['', 'local', 'other', '\ud800', '😀']) {
    for (const actual of [null, '', 'local', 'other', '\ud800', '😀']) {
      for (const kind of ['conflict', 'committed', 'refused', 'unknown']) {
        const outcome = Object.freeze({ kind, actual, version: 'existing', untouched: 'preserve' });
        const intent = Object.freeze({ local, untouched: 'preserve' });
        const result = sandbox.subject(outcome, intent);
        const promote = kind === 'conflict' && actual !== null && actual === local;
        const conforms = promote ? result !== outcome && result.kind === 'committed' && result.version === local : result === outcome;
        fixtures.push({ kind, actual, local, conforms, sameObject: result === outcome, resultKind: result.kind, resultVersion: result.version });
      }
    }
  }
  // Exercise non-conflicts without an actual field, as allowed by real Outcome variants.
  for (const kind of ['committed', 'refused', 'unknown']) {
    const input = Object.freeze({ kind });
    const result = sandbox.subject(input, Object.freeze({ local: 'local' }));
    fixtures.push({ kind, missingActual: true, conforms: result === input, sameObject: result === input });
  }
  const differences = fixtures.filter(row => !row.conforms);
  if (['wrong-comparison', 'wrong-version', 'unconditional-promotion'].includes(name) ? !differences.length : differences.length) fail('Unexpected native policy result: ' + name);
  writeFileSync(resolve(directory, 'native-fixtures.json'), JSON.stringify(fixtures, null, 2) + '\n');
  receipt.variants[name] = { sourceSha256: hash(text), emittedSha256: hash(emitted), cases: fixtures.length,
    differences: differences.length, firstCounterexample: differences[0] ?? null,
    unrelatedHeadWitness: differences.find(row => row.kind === 'conflict' && row.actual === 'other' && row.local === 'local') ?? null,
    matchingHeadWitness: fixtures.find(row => row.kind === 'conflict' && row.actual === 'local' && row.local === 'local') };
}
if (receipt.variants.base.emittedSha256 !== receipt.variants['equivalent-layout'].emittedSha256) fail('Layout control changed canonical emitted program');
if (receipt.variants.base.emittedSha256 === receipt.variants['equivalent-null-check'].emittedSha256) fail('Semantic equivalence control must change emitted program');
writeFileSync(resolve(outputPath, 'preparation.json'), JSON.stringify(receipt, null, 2) + '\n');
console.log(JSON.stringify(receipt, null, 2));
