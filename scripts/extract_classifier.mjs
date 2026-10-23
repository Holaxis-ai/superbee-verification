import ts from 'typescript';
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { resolve, dirname } from 'node:path';
import vm from 'node:vm';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const [sourcePath, outputPath, variant = 'base'] = process.argv.slice(2);
const fail = message => { throw new Error(message); };
const hash = value => createHash('sha256').update(value).digest('hex');
const units = text => Array.from({ length: text.length }, (_, index) => text.charCodeAt(index));
const leanText = text => `[${units(text).join(', ')}]`;
const pin = JSON.parse(readFileSync(resolve(root, 'experiments/source-classifier/source-pin.json'), 'utf8'));
let source = readFileSync(sourcePath, 'utf8');
if (hash(source) !== pin.sha256) fail('Source pin mismatch');
if (!['base', 'and-to-or', 'wrong-code', 'unsupported-call'].includes(variant)) fail('Unknown controlled variant');
if (ts.version !== '5.9.3') fail('Unexpected TypeScript parser version');

function declarations(text) {
  const file = ts.createSourceFile(pin.path, text, ts.ScriptTarget.ES2022, true, ts.ScriptKind.TS);
  if (file.parseDiagnostics.length) fail('Source parse diagnostics');
  const functions = file.statements.filter(node => ts.isFunctionDeclaration(node) && node.name?.text === pin.function);
  if (functions.length !== 1) fail('Expected exactly one function');
  const fn = functions[0];
  if (fn.asteriskToken || fn.modifiers?.some(m => m.kind !== ts.SyntaxKind.ExportKeyword) ||
      fn.parameters.length !== 1 || !ts.isIdentifier(fn.parameters[0].name) || fn.parameters[0].initializer ||
      fn.parameters[0].modifiers?.length || fn.parameters[0].dotDotDotToken || fn.parameters[0].questionToken ||
      fn.body?.statements.length !== 1 || !ts.isReturnStatement(fn.body.statements[0]) || !fn.body.statements[0].expression)
    fail('Unsupported function shape');
  const bindings = file.statements.filter(ts.isVariableStatement).flatMap(statement => statement.declarationList.declarations
    .filter(d => ts.isIdentifier(d.name) && d.name.text === pin.binding).map(decl => ({ statement, decl })));
  if (bindings.length !== 1) fail('Expected exactly one set binding');
  const { statement, decl } = bindings[0];
  const value = decl.initializer;
  if (!(statement.declarationList.flags & ts.NodeFlags.Const) || statement.declarationList.declarations.length !== 1 ||
      !value || !ts.isNewExpression(value) || !ts.isIdentifier(value.expression) || value.expression.text !== 'Set' ||
      value.arguments?.length !== 1 || !ts.isArrayLiteralExpression(value.arguments[0]) ||
      !value.arguments[0].elements.every(ts.isStringLiteral)) fail('Unsupported native set initialization');
  return { file, fn, statement, literals: value.arguments[0].elements, expr: fn.body.statements[0].expression };
}

const initial = declarations(source);
if (variant === 'and-to-or') {
  if (!ts.isBinaryExpression(initial.expr) || initial.expr.operatorToken.kind !== ts.SyntaxKind.AmpersandAmpersandToken) fail('Expected source AND');
  const operator = initial.expr.operatorToken;
  source = source.slice(0, operator.getStart(initial.file)) + '||' + source.slice(operator.end);
} else if (variant === 'wrong-code') {
  const literal = initial.literals.find(node => node.text === 'FORBIDDEN');
  if (!literal) fail('Missing controlled code');
  source = source.slice(0, literal.getStart(initial.file)) + '"NOT_FORBIDDEN"' + source.slice(literal.end);
} else if (variant === 'unsupported-call') {
  source = source.slice(0, initial.expr.getStart(initial.file)) + 'console.log("unsupported")' + source.slice(initial.expr.end);
}
const { file, fn, statement, literals, expr } = declarations(source);
const parameter = fn.parameters[0].name.text;
function field(node) {
  if (!ts.isPropertyAccessExpression(node) || node.questionDotToken || !ts.isIdentifier(node.expression) || node.expression.text !== parameter ||
      !['kind', 'code'].includes(node.name.text)) fail('Unsupported plain field');
  return node.name.text;
}
function lower(node) {
  if (ts.isParenthesizedExpression(node)) return lower(node.expression);
  if (node.kind === ts.SyntaxKind.TrueKeyword) return '(.literal true)';
  if (node.kind === ts.SyntaxKind.FalseKeyword) return '(.literal false)';
  if (ts.isBinaryExpression(node)) {
    if (node.operatorToken.kind === ts.SyntaxKind.AmpersandAmpersandToken || node.operatorToken.kind === ts.SyntaxKind.BarBarToken)
      return `(.${node.operatorToken.kind === ts.SyntaxKind.AmpersandAmpersandToken ? 'and' : 'or'} ${lower(node.left)} ${lower(node.right)})`;
    if (node.operatorToken.kind === ts.SyntaxKind.EqualsEqualsEqualsToken && ts.isStringLiteral(node.right))
      return `(.eq .${field(node.left)} ${leanText(node.right.text)})`;
  }
  if (ts.isCallExpression(node) && !node.questionDotToken && node.arguments.length === 1 && ts.isPropertyAccessExpression(node.expression) &&
      !node.expression.questionDotToken && ts.isIdentifier(node.expression.expression) && node.expression.expression.text === pin.binding &&
      node.expression.name.text === 'has') return `(.has .${field(node.arguments[0])})`;
  fail(`Unsupported expression: ${ts.SyntaxKind[node.kind]}`);
}
const program = lower(expr);
const codes = literals.map(node => node.text);
mkdirSync(outputPath, { recursive: true });
writeFileSync(resolve(outputPath, 'SourceGenerated.lean'), `import Bridge.Semantics\nnamespace SourceGenerated\ndef program : SourceBridge.Expr := ${program}\ndef codes : List SourceBridge.Text := [${codes.map(leanText).join(', ')}]\nend SourceGenerated\n`);
writeFileSync(resolve(outputPath, 'source-function.ts'), statement.getText(file) + '\n\n' + fn.getText(file) + '\n');
const emitted = ts.transpileModule(statement.getText(file) + '\n' + fn.getText(file), {
  compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.CommonJS }, reportDiagnostics: true,
});
if (emitted.diagnostics?.some(row => row.category === ts.DiagnosticCategory.Error)) fail('Transpile diagnostic');
writeFileSync(resolve(outputPath, 'source-function.js'), emitted.outputText);
// This executes only the already-whitelisted pure fragment. vm is not a security boundary.
const sandbox = { exports: {} };
vm.runInNewContext(emitted.outputText, sandbox, { timeout: 1000 });
const policy = ['AUTH_REQUIRED', 'FORBIDDEN', 'UNAUTHORIZED', 'PERMISSION_DENIED', 'REQUEST_CAPACITY_PRINCIPAL', 'REQUEST_CAPACITY_BUNDLE'];
const kinds = ['refused', 'committed', 'conflict', 'unknown', '', '\ud800', '\udfff', '😀'];
const testCodes = [undefined, ...policy, 'NOT_FORBIDDEN', '', 'other', '\ud800', '\udfff', '😀'];
let differences = 0;
const fixtures = [];
for (const kind of kinds) for (const code of testCodes) {
  const input = code === undefined ? { kind } : { kind, code };
  const result = sandbox.exports[pin.function](input);
  const expected = kind === 'refused' && policy.includes(code);
  if (result !== expected) differences++;
  fixtures.push({ kind: units(kind), code: code === undefined ? null : units(code), actual: result });
}
for (const kind of kinds) {
  const actual = sandbox.exports[pin.function]({ kind, code: undefined });
  if (actual !== false) differences++;
  fixtures.push({ kind: units(kind), code: null, actual });
}
writeFileSync(resolve(outputPath, 'native-fixtures.json'), JSON.stringify(fixtures, null, 2) + '\n');
const receipt = { variant, node: process.version, parser: ts.version, upstream: pin, inputSha256: hash(source), functionSha256: hash(fn.getText(file)),
  generatedSha256: hash(readFileSync(resolve(outputPath, 'SourceGenerated.lean'))), emittedJsSha256: hash(emitted.outputText),
  program, codes, nativeFixtureCount: fixtures.length, nativePolicyDifferences: differences,
  trust: 'parser/lowering and restricted semantics trusted; native fixtures are not proof of JavaScript engine conformance' };
writeFileSync(resolve(outputPath, 'extraction.json'), JSON.stringify(receipt, null, 2) + '\n');
console.log(JSON.stringify(receipt));
