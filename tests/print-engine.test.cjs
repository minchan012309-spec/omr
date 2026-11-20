const {test}=require('node:test');const assert=require('node:assert/strict');const fs=require('node:fs');
const p=require('node:path').join(__dirname,'../lib/print-engine.js');
test('old records stay HTML, new records use HTML and previous QR metadata stays readable',()=>{
 assert.ok(fs.existsSync(p),'출력 엔진 구분 모듈이 필요합니다');const e=require(p);
 assert.equal(e.engine({}),'html');assert.equal(e.engine({t:Date.now()}),'html');
 const n=e.fresh();assert.equal(e.engine(n),'html');assert.equal(n.printEngine,'html');assert.equal(e.engine({printEngine:'xelatex-v1'}),'xelatex-v1');
 assert.equal(e.engine({...n,title:'수정'}),'html');
 assert.throws(()=>e.engine({printEngine:'future'}),/지원/);
});
test('versioned new book IDs do not overwrite legacy configuration IDs',()=>{
 assert.ok(fs.existsSync(p));const e=require(p);const id=e.bookId('cm-xen20');
 assert.match(id,/^cm-xen20~l[0-9a-f]{16}$/);assert.equal(e.sourceBookId(id+'r3~g1'),'cm-xen20r3~g1');
 assert.equal(e.sourceBookId('cm-xen20r3'),'cm-xen20r3');
});

test('all changed application scripts parse before browser loading',()=>{const vm=require('node:vm'),path=require('node:path');for(const file of ['books.js','lib/print-engine.js','lib/latex/document.js','lib/latex/local.js','lazy/latex-print.js'])assert.doesNotThrow(()=>new vm.Script(fs.readFileSync(path.join(__dirname,'..',file),'utf8'),{filename:file}))});
