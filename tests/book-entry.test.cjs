const {test}=require('node:test');
const assert=require('node:assert/strict');
const vm=require('node:vm');
const fs=require('node:fs');
const src=fs.readFileSync('books.js','utf8');
function harness(){
 const start=src.indexOf('let BKENTRY=null;'),end=src.indexOf('function bkPageNums',start);
 assert.ok(start>=0,'Book entry must have a shared loading and duplicate-click guard');
 const events=[];
 const ctx={setTimeout, busyRun:async(label,fn)=>{events.push('loading');try{return await fn()}finally{events.push('idle')}},events};
 vm.createContext(ctx);vm.runInContext(src.slice(start,end),ctx);return ctx;
}
test('repeated grading clicks run once and show loading before preparing content',async()=>{
 const h=harness();let release,calls=0;
 const work=()=>{calls++;h.events.push('work');return new Promise(r=>release=r)};
 const a=h.bkEntryRun('준비',work),b=h.bkEntryRun('준비',work);
 assert.equal(a,b);assert.deepEqual(h.events,['loading']);
 await new Promise(r=>setTimeout(r,50));assert.equal(calls,1);
 release(7);assert.equal(await a,7);assert.deepEqual(h.events,['loading','work','idle']);
 assert.equal(await h.bkEntryRun('다시',async()=>8),8);
});
test('a failed grading request releases the guard for retry',async()=>{
 const h=harness();await assert.rejects(h.bkEntryRun('준비',async()=>{throw Error('offline')}));
 assert.equal(await h.bkEntryRun('재시도',async()=>9),9);
});
function browseHarness(access=true){
 const ctx={BKENTRY:null,BKV:{},tab:'books',bkEntryRun:(_l,f)=>f(),bkxAccess:async()=>access,bkPid:x=>x,bkPlan:async()=>({pages:[]}),bkBrowseView:()=>{}};
 vm.createContext(ctx);const start=src.indexOf('let BKNAVSEQ=0;');vm.runInContext(src.slice(start,src.indexOf('function bkBrowseStep',start)),ctx);return ctx;
}
test('browse access failure leaves a recoverable error state',async()=>{
 const h=browseHarness(false);await h.bkBrowseStart('me-c');assert.equal(h.BKV.error,true);
});
test('leaving the books tab during preparation retains the completed plan',async()=>{
 const h=browseHarness();let release,started;const planning=new Promise(r=>started=r);h.bkPlan=()=>new Promise(r=>{release=r;started()});
 const task=h.bkBrowseStart('me-c');await planning;h.tab='grade';release({title:'교재',pages:[]});await task;
 assert.equal(h.BKV.plan.title,'교재');
});
