import ts from 'typescript';
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { isDeepStrictEqual } from 'node:util';
import vm from 'node:vm';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const [sourcePath, outputPath] = process.argv.slice(2);
const hash = value => createHash('sha256').update(value).digest('hex');
const fail = message => { throw new Error(message); };
if (!sourcePath || !outputPath) fail('Usage: prepare_retry.mjs SOURCE OUTPUT');
const pin = JSON.parse(readFileSync(resolve(root, 'experiments/gillian-retry/source-pin.json')));
const raw = readFileSync(sourcePath);
if (hash(raw) !== pin.sha256) fail('Source pin mismatch');
if (ts.version !== '5.9.3') fail('Wrong TypeScript version');
const file = ts.createSourceFile(pin.path, raw.toString('utf8'), ts.ScriptTarget.ES2022, true, ts.ScriptKind.TS);
if (file.parseDiagnostics.length) fail('Source parse diagnostics');
const functions = file.statements.filter(node => ts.isFunctionDeclaration(node) && node.name?.text === pin.function);
if (functions.length !== 1) fail('Function selection mismatch');
const declaration = raw.subarray(pin.declarationByteSpan.start, pin.declarationByteSpan.end).toString('utf8');
if (declaration !== functions[0].getText(file) || !declaration.startsWith('export function ')) fail('Independent span mismatch');
const base = declaration.slice('export '.length);
function replaceOnce(text, before, after) {
  if (text.split(before).length !== 2) fail('Ambiguous mutation anchor: ' + before);
  return text.replace(before, after);
}
const variants = {
  base,
  'gap-admission': replaceOnce(base, ') === row.attempts', ') <= row.attempts'),
  'always-deny': replaceOnce(base, 'return row.receipt === undefined && (row.state === "pending" || row.state === "unknown") && (row.notAppliedThrough ?? 0) === row.attempts;', 'return false;'),
  'always-allow': replaceOnce(base, 'return row.receipt === undefined && (row.state === "pending" || row.state === "unknown") && (row.notAppliedThrough ?? 0) === row.attempts;', 'return true;'),
  'unknown-to-inflight': replaceOnce(base, 'row.state === "unknown"', 'row.state === "in_flight"'),
  'receipt-bypass': replaceOnce(base, 'row.receipt === undefined && ', ''),
  'state-bypass': replaceOnce(base, '(row.state === "pending" || row.state === "unknown") && ', ''),
  'equivalent-state-order': replaceOnce(base, 'row.state === "pending" || row.state === "unknown"', 'row.state === "unknown" || row.state === "pending"'),
  'equivalent-layout': replaceOnce(base, '  return ', '  /* harmless layout */\n    return   '),
};
function emit(text) {
  const result = ts.transpileModule(text, { compilerOptions: { target: ts.ScriptTarget.ES5, module: ts.ModuleKind.CommonJS,
    removeComments: true, alwaysStrict: true }, reportDiagnostics: true });
  if (result.diagnostics?.some(d => d.category === ts.DiagnosticCategory.Error)) fail('Type erasure diagnostics: ' + result.diagnostics.map(d => ts.flattenDiagnosticMessageText(d.messageText, ' ')).join('; '));
  return result.outputText;
}
const maximum = Number.MAX_SAFE_INTEGER;
const numbers = [['zero', 0], ['negative-zero', -0], ['one', 1], ['two', 2], ['maximum-minus-one', maximum - 1], ['maximum', maximum]];
const prefixes = [['missing', undefined], ['undefined', undefined], ['null', null], ...numbers];
const receipts = ['missing', 'undefined', 'object', 'null'];
const states = ['pending', 'unknown', 'in_flight', 'acknowledged', 'conflict', 'refused', 'other'];
mkdirSync(outputPath, { recursive: true });
const receipt = { pin, parser: ts.version, node: process.version,
  domain: 'Ordinary extensible Object.prototype records with writable/enumerable/configurable own data fields. Projection labels do not establish payload/evidence validation or transition reachability. Null receipt/prefix are defensive invalid-record cases.',
  variants: {} };
for (const [name, text] of Object.entries(variants)) {
  if (name !== 'base' && text === base) fail('Mutation did not change source: ' + name);
  const emitted = emit(text);
  const directory = resolve(outputPath, name);
  mkdirSync(directory, { recursive: true });
  writeFileSync(resolve(directory, 'source.ts'), text + '\n');
  writeFileSync(resolve(directory, 'subject.js'), emitted);
  const sandbox = {};
  // vm executes only this pinned compiler output; it is not a security boundary.
  vm.runInNewContext(emitted + '\nthis.subject = blobIntentResendable;', sandbox, { timeout: 1000 });
  const fixtures = [];
  for (const receiptCase of receipts) for (const state of states) for (const [prefixCase, prefix] of prefixes) for (const [attemptCase, attempts] of numbers) {
    const row = { state, attempts, untouched: { marker: 'preserve' } };
    if (receiptCase !== 'missing') row.receipt = receiptCase === 'object' ? { marker: 'receipt-projection' } : receiptCase === 'null' ? null : undefined;
    if (prefixCase !== 'missing') row.notAppliedThrough = prefix;
    const before = structuredClone(Object.getOwnPropertyDescriptors(row));
    const prototype = Object.getPrototypeOf(row), extensible = Object.isExtensible(row);
    // Policy is expressed independently from the source expression, by fixture categories.
    const noReceipt = receiptCase === 'missing' || receiptCase === 'undefined';
    const eligibleState = ['pending', 'unknown'].includes(state);
    const normalizedPrefix = ['missing', 'undefined', 'null'].includes(prefixCase) ? 0 : prefix;
    const expected = noReceipt && eligibleState && normalizedPrefix === attempts;
    const result = sandbox.subject(row);
    const framePreserved = isDeepStrictEqual(before, Object.getOwnPropertyDescriptors(row)) && prototype === Object.getPrototypeOf(row) && extensible === Object.isExtensible(row);
    const terminal = ['acknowledged', 'conflict', 'refused'].includes(state);
    const capturedFieldProjection = state !== 'other' && prefixCase !== 'null' && receiptCase !== 'null' && terminal === !noReceipt && normalizedPrefix <= attempts;
    fixtures.push({ receiptCase, state, prefixCase, attemptCase, prefix: prefixCase === 'missing' || prefixCase === 'undefined' ? null : prefix,
      attempts, expected, result, framePreserved, conforms: typeof result === 'boolean' && result === expected && framePreserved,
      domain: capturedFieldProjection ? 'captured-valid-field-projection-only' : 'defensive-or-invalid-field-projection' });
  }
  const differences = fixtures.filter(row => !row.conforms);
  const bad = ['gap-admission', 'always-deny', 'always-allow', 'unknown-to-inflight', 'receipt-bypass', 'state-bypass'].includes(name);
  if (bad ? !differences.length : differences.length) fail('Unexpected native policy result: ' + name);
  const select = (state, attemptCase, prefixCase) => fixtures.find(row => row.receiptCase === 'missing' && row.state === state && row.attemptCase === attemptCase && row.prefixCase === prefixCase);
  const witnesses = {
    ambiguousUnknown: select('unknown', 'one', 'zero'),
    coveredUnknown: select('unknown', 'one', 'one'),
    initialPending: select('pending', 'zero', 'missing'),
    inFlightDenied: select('in_flight', 'zero', 'missing'),
    maximumEligibilityNotClaimGuarantee: select('pending', 'maximum', 'maximum'),
    receiptBypassDefensiveOnly: fixtures.find(row => row.receiptCase === 'object' && row.state === 'pending' && row.attemptCase === 'zero' && row.prefixCase === 'missing'),
  };
  if (name === 'gap-admission' && (witnesses.ambiguousUnknown.result !== true || witnesses.ambiguousUnknown.expected !== false)) fail('Missing genuine ambiguity witness');
  if (name === 'always-deny' && witnesses.initialPending.conforms) fail('Vacuity control lacks positive failure');
  if (name === 'unknown-to-inflight' && (witnesses.coveredUnknown.conforms || witnesses.inFlightDenied.conforms)) fail('State mutation lacks both witnesses');
  if (name === 'receipt-bypass' && (witnesses.receiptBypassDefensiveOnly.conforms || witnesses.receiptBypassDefensiveOnly.domain !== 'defensive-or-invalid-field-projection')) fail('Receipt mutation lacks defensive-domain witness');
  if (name === 'state-bypass' && (witnesses.inFlightDenied.conforms || witnesses.inFlightDenied.domain !== 'captured-valid-field-projection-only')) fail('State bypass lacks captured-field-projection witness');
  writeFileSync(resolve(directory, 'native-fixtures.json'), JSON.stringify(fixtures, null, 2) + '\n');
  receipt.variants[name] = { sourceSha256: hash(text), emittedSha256: hash(emitted), cases: fixtures.length,
    differences: differences.length, capturedFieldProjectionDifferences: differences.filter(row => row.domain === 'captured-valid-field-projection-only').length,
    firstCounterexample: differences[0] ?? null, witnesses };
}
if (receipt.variants.base.emittedSha256 !== receipt.variants['equivalent-layout'].emittedSha256) fail('Layout control changed canonical emitted program');
if (receipt.variants.base.emittedSha256 === receipt.variants['equivalent-state-order'].emittedSha256) fail('Semantic equivalence control must change emitted program');
writeFileSync(resolve(outputPath, 'preparation.json'), JSON.stringify(receipt, null, 2) + '\n');
console.log(JSON.stringify(receipt, null, 2));
