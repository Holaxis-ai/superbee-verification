import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import { createHash } from 'node:crypto';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';
import { execFileSync } from 'node:child_process';

const argv = process.argv.slice(2);
const option = name => { const i = argv.indexOf(name); assert(i >= 0 && argv[i+1]); return path.resolve(argv[i+1]); };
const product = option('--source-root'), out = option('--out-dir');
const pins = JSON.parse(await fs.readFile(new URL('../experiments/production-retirement/pins.json', import.meta.url)));
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
assert.equal(process.version, pins.node);
assert.equal(execFileSync('git', ['rev-parse','HEAD'], {cwd:product, encoding:'utf8'}).trim(), pins.product_revision);
for (const [file, digest] of Object.entries(pins.product_files)) assert.equal(hash(await fs.readFile(path.join(product,file))), digest, `source drift: ${file}`);
const require = createRequire(path.join(product,'package.json'));
const ts = require('typescript'); assert.equal(ts.version,pins.typescript);
assert.equal(hash(await fs.readFile(require.resolve('typescript'))), pins.typescript_sha256);
assert.equal(JSON.parse(await fs.readFile(path.join(product,'node_modules/fake-indexeddb/package.json'),'utf8')).version, pins.fake_indexeddb);
const { IDBFactory } = require('fake-indexeddb');
const compiler = ts.readConfigFile(path.join(product,'packages/core/tsconfig.json'),ts.sys.readFile);
assert(!compiler.error);
const config = ts.parseJsonConfigFileContent(compiler.config,ts.sys,path.join(product,'packages/core'));
assert.equal(config.errors.length,0);
await fs.mkdir(path.dirname(out),{recursive:true});
await fs.mkdir(out,{recursive:false});
const modules=['journaled-backend','file-journaled-backend','indexeddb-backend'];
function emit(overrides) {
  const host=ts.createCompilerHost(config.options), read=host.readFile;
  host.getCurrentDirectory=()=>product;
  host.readFile = file => overrides.get(path.resolve(file)) ?? read(file);
  const emitted=new Map(); const program=ts.createProgram(config.fileNames,config.options,host);
  const diagnostics=ts.getPreEmitDiagnostics(program);
  assert.equal(diagnostics.length,0,ts.formatDiagnosticsWithColorAndContext(diagnostics,host));
  const result=program.emit(undefined,(file,text)=>{if(file.endsWith('.js'))emitted.set(path.resolve(file),text);});
  assert(!result.emitSkipped); return emitted;
}
const baseline=emit(new Map());
for (const [file,text] of baseline) assert.equal(await fs.readFile(file,'utf8'),text,`unmodified compiler emission mismatch: ${file}`);
const sourceMap = new Map(await Promise.all(modules.map(async name => [name,await fs.readFile(path.join(product,`packages/core/src/${name}.ts`),'utf8')])));
function replaceOnce(text, before, after) { assert.equal(text.split(before).length-1,1,`mutation selector not unique: ${before}`); return text.replace(before,after); }
const variants=['baseline','equivalent','guard-bypass','allow-unacknowledged','overbroad-removal','caller-alias'];
function sources(variant) {
  const map=new Map(sourceMap);
  if(variant==='equivalent') map.set('journaled-backend',replaceOnce(map.get('journaled-backend'),'if (!equalJournalValue(a, b)) throw new JournalGuardConflict(a.target);','if (equalJournalValue(a, b) === false) throw new JournalGuardConflict(a.target);'));
  if(variant==='guard-bypass') map.set('journaled-backend',replaceOnce(map.get('journaled-backend'),'if (!equalJournalValue(a, b)) throw new JournalGuardConflict(a.target);','if (false) throw new JournalGuardConflict(a.target);'));
  if(variant==='allow-unacknowledged') map.set('journaled-backend',replaceOnce(map.get('journaled-backend'),'ids.some(id => guard.intents.find(row => row.requestId === id)?.state !== "acknowledged")','false'));
  if(variant==='caller-alias') map.set('journaled-backend',replaceOnce(map.get('journaled-backend'),'const captured = captureJournalValue({ requestIds: options.requestIds, removeMeta: options.removeMeta });','const captured = { requestIds: options.requestIds, removeMeta: options.removeMeta };'));
  if(variant==='overbroad-removal') {
    map.set('file-journaled-backend',replaceOnce(map.get('file-journaled-backend'),'const changes: Change[] = requestIds.map((key): Change => ({ family: "intent", key, value: null }));','const changes: Change[] = guard.intents.map(row => row.requestId).map((key): Change => ({ family: "intent", key, value: null }));'));
    const text=map.get('indexeddb-backend'), begin=text.indexOf('  async retireAcknowledged('), end=text.indexOf('\n  /** Read and compare a complete guard',begin);
    assert(begin>=0 && end>begin); const region=replaceOnce(text.slice(begin,end),'for (const requestId of requestIds) {','for (const requestId of expected.intents.map(row => row.requestId)) {');
    map.set('indexeddb-backend',text.slice(0,begin)+region+text.slice(end));
  }
  return map;
}
// Tags preserve undefined, complete object keys and primitive kinds. The fixture
// domain deliberately excludes symbols/accessors/holes/non-safe numbers/host values.
function tag(value) {
  if(value===undefined)return ['undefined']; if(value===null)return ['null'];
  if(typeof value==='string')return ['string',value];
  if(typeof value==='boolean')return ['boolean',value];
  if(typeof value==='number'){assert(Number.isSafeInteger(value)&&value>=0&&!Object.is(value,-0));return ['natural',value];}
  assert.equal(typeof value,'object'); assert(!Object.getOwnPropertySymbols(value).length);
  if(Array.isArray(value)) {
    assert.deepEqual(Reflect.ownKeys(value),[...Array(value.length).keys()].map(String).concat('length'));
    for(let i=0;i<value.length;i++){const d=Object.getOwnPropertyDescriptor(value,String(i));assert(d.enumerable&&'value'in d);}
    return ['array',value.map(tag)];
  }
  assert.equal(Object.getPrototypeOf(value),Object.prototype);
  assert.equal(Reflect.ownKeys(value).length,Object.keys(value).length);
  return ['object',Object.keys(value).sort().map(key=>{const d=Object.getOwnPropertyDescriptor(value,key);assert(d.enumerable&&'value'in d);return [key,tag(d.value)];})];
}
const target='pilot/target', foreign='pilot/foreign';
const keys=['evidence','undefined-value','missing','unnamed'];
const names=['multi-reopen','queued-caller-alias','same-version-stale-raw','same-raw-stale-version','retained-ack-residual','pending-residual','absent-v-undefined','select-pending','named-absent-removal','guard-permutation','duplicate-selection','unscoped-meta','missing-ack-history','stale-named-value'];
function document(id,body){return {id,frontmatter:{type:'Pilot'},body};}
function intent(id,idTarget,base){return {requestId:id,kind:'document.write',target:idTarget,base,baseContent:null,createdAt:'2026-10-23T00:00:00.000Z'};}
async function full(backend) {
  const read=await backend.readWithJournal(target,{meta:keys});
  const other=await backend.readWithJournal(foreign);
  return {target,document:read.document?{version:read.document.version,raw:read.raw}:null,
    records:await backend.listIntents(), metadata:keys.filter(key=>read.meta.has(key)).map(key=>[key,read.meta.get(key)]),
    foreignDocument:other.document?{version:other.document.version,raw:other.raw}:null};
}
function guardOf(before) {return {target,document:structuredClone(before.document),intents:structuredClone(before.records.filter(row=>row.target===target)),
  meta:keys.filter(key=>key!=='unnamed').map(key=>{const found=before.metadata.find(row=>row[0]===key);return {key,expected:found?{present:true,value:structuredClone(found[1])}:{present:false}};})};}
async function runCase(kind,name,File,Indexed) {
  const directory=await fs.mkdtemp(path.join(os.tmpdir(),'retirement-production-'));
  const factory=new IDBFactory(); const databaseName='pilot';
  const open=()=>kind==='file'?File.open({directory,lock:{lockRoot:path.join(directory,'locks')}}):Promise.resolve(new Indexed({databaseName,indexedDB:factory}));
  let backend=await open();
  try {
    await backend.writeReserved('','index.md',"---\nokf_version: '0.2'\n---\n");
    let base=null;
    for(const id of ['ack-one','ack-two','keep-ack','outstanding']) {
      const result=await backend.writeJournaled(target,document(target,id),{intent:intent(id,target,base),...(id==='ack-one'?{meta:[{key:'evidence',value:{note:'retained',values:[1,undefined]}},{key:'undefined-value',value:undefined},{key:'unnamed',value:'must remain'}]}:{})});
      base=result.version;
      if(id!=='outstanding')await backend.updateIntent(id,'pending',{state:'acknowledged',attempts:1,acknowledgedVersion:result.version});
    }
    const f=await backend.writeJournaled(foreign,document(foreign,'foreign'),{intent:intent('foreign-ack',foreign,null)});
    await backend.updateIntent('foreign-ack','pending',{state:'acknowledged',attempts:1,acknowledgedVersion:f.version});
    const before=await full(backend), guard=guardOf(before);
    const options={guard,requestIds:['ack-one'],removeMeta:['evidence']};
    if(name==='multi-reopen'||name==='queued-caller-alias'){options.requestIds=['ack-one','ack-two'];options.removeMeta=['evidence','undefined-value'];}
    if(name==='same-version-stale-raw')guard.document.raw+=' stale';
    if(name==='same-raw-stale-version')guard.document.version+='stale';
    if(name==='retained-ack-residual')guard.intents.find(row=>row.requestId==='keep-ack').baseContent='stale residual';
    if(name==='pending-residual')guard.intents.find(row=>row.requestId==='outstanding').baseContent='stale residual';
    if(name==='absent-v-undefined')guard.meta.find(row=>row.key==='undefined-value').expected={present:false};
    if(name==='select-pending')options.requestIds=['outstanding'];
    if(name==='named-absent-removal')options.removeMeta=['missing'];
    if(name==='guard-permutation'){guard.intents.reverse();guard.meta.reverse();}
    if(name==='duplicate-selection')options.requestIds=['ack-one','ack-one'];
    if(name==='unscoped-meta')options.removeMeta=['unnamed'];
    if(name==='missing-ack-history')guard.intents=guard.intents.filter(row=>row.requestId!=='keep-ack');
    if(name==='stale-named-value')guard.meta.find(row=>row.key==='evidence').expected={present:true,value:{note:'different'}};
    const original=structuredClone(options);
    let outcome='accepted',error=null;
    try {
      const pending=backend.retireAcknowledged(target,options);
      if(name==='queued-caller-alias'){options.requestIds[0]='outstanding';options.removeMeta[0]='unnamed';options.guard.document.raw+='caller mutation';}
      await pending;
    } catch(e) {outcome='refused';error={name:e.name,message:e.message};assert.equal(e.name,'JournalGuardConflict');}
    const after=await full(backend);
    await backend.close(); backend=await open(); const reopened=await full(backend);
    const expectedAccepted=['multi-reopen','queued-caller-alias','named-absent-removal','guard-permutation'].includes(name);
    const same=(a,b)=>JSON.stringify(tag(a))===JSON.stringify(tag(b));
    const violations=[];
    if((outcome==='accepted')!==expectedAccepted)violations.push('fixture-outcome');
    if(!same(after,reopened))violations.push('reopen-state');
    if(outcome==='refused'&&!same(before,after))violations.push('refusal-mutated-state');
    if(outcome==='accepted'){
      if(!same(after.records,before.records.filter(row=>!original.requestIds.includes(row.requestId))))violations.push('exact-record-frame');
      if(!same(after.metadata,before.metadata.filter(row=>!(original.removeMeta??[]).includes(row[0]))))violations.push('exact-metadata-frame');
      if(!same(after.document,before.document)||!same(after.foreignDocument,before.foreignDocument))violations.push('document-frame');
    }
    const removedIds=before.records.filter(row=>!after.records.some(r=>r.requestId===row.requestId)).map(row=>row.requestId);
    const removedMeta=before.metadata.filter(row=>!after.metadata.some(r=>r[0]===row[0])).map(row=>row[0]);
    return {adapter:kind,name,outcome,error,hostViolations:violations,before:tag(before),options:tag(original),after:tag(after),reopened:tag(reopened),actualRemovedIds:removedIds,actualRemovedMeta:removedMeta};
  } finally {await backend.close();await fs.rm(directory,{recursive:true,force:true});}
}
const report={v:1,node:process.version,typescript:ts.version,typescriptSha256:hash(await fs.readFile(require.resolve('typescript'))),fakeIndexedDB:JSON.parse(await fs.readFile(path.join(product,'node_modules/fake-indexeddb/package.json'),'utf8')).version,product_revision:pins.product_revision,
  compiler_options:config.options,unmodified_emission_matches:true,emitted_module_count:baseline.size,baseline_module_hashes:Object.fromEntries([...baseline].map(([file,text])=>[path.relative(path.join(product,'packages/core/dist'),file),hash(text)])),variants:[]};
for(const variant of variants) {
  const folder=path.join(out,variant);await fs.mkdir(folder);
  const dist=path.join(folder,'dist');await fs.cp(path.join(product,'packages/core/dist'),dist,{recursive:true});
  await fs.writeFile(path.join(folder,'package.json'),'{"type":"module"}');
  await fs.symlink(path.join(product,'node_modules'),path.join(folder,'node_modules'),'dir');
  const selected=sources(variant);
  for(const [name,text]of selected)await fs.writeFile(path.join(folder,name+'.ts'),text);
  const overrides=new Map([...selected].map(([name,text])=>[path.join(product,`packages/core/src/${name}.ts`),text]));
  const emitted=variant==='baseline'?baseline:emit(overrides),changed=[];
  for(const [file,text]of emitted)if(text!==baseline.get(file)) {const name=path.basename(file);assert(modules.some(module=>name===module+'.js'));await fs.writeFile(path.join(dist,name),text);changed.push(name);}
  const File=(await import(pathToFileURL(path.join(dist,'file-journaled-backend.js')))).FileJournaledBackend;
  const Indexed=(await import(pathToFileURL(path.join(dist,'indexeddb-backend.js')))).IndexedDbBackend;
  const seam=await import(pathToFileURL(path.join(dist,'journaled-backend.js')));
  assert.equal(typeof seam.captureRetireAcknowledged,'function'); assert.equal(typeof seam.assertJournalGuard,'function');
  const results=[];
  for(const adapter of ['file','indexeddb'])for(const name of names)results.push(await runCase(adapter,name,File,Indexed));
  const identities={source:Object.fromEntries([...selected].map(([name,text])=>[name,hash(text)])),modules:Object.fromEntries(await Promise.all(modules.map(async name=>[name,hash(await fs.readFile(path.join(dist,name+'.js')))])))};
  report.variants.push({name:variant,changed_modules:changed,identities,results});
  await fs.writeFile(path.join(out,'observations.json'),JSON.stringify(report,null,2)+'\n');
  console.log(`${variant}: ${results.length} actual adapter executions completed; ${results.filter(r=>r.hostViolations.length).length} observed law violations`);
  if(['baseline','equivalent'].includes(variant))assert(results.every(r=>r.hostViolations.length===0),'baseline/equivalent law failure');
  else for(const adapter of ['file','indexeddb'])assert(results.some(r=>r.adapter===adapter&&r.hostViolations.length>0),'mutant did not alter observed law');
  await fs.rm(dist,{recursive:true,force:true}); await fs.unlink(path.join(folder,'node_modules'));
}

for (const [file,digest] of Object.entries(pins.product_files)) assert.equal(hash(await fs.readFile(path.join(product,file))),digest,`source changed during run: ${file}`);
