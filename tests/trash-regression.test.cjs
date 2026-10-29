const { test } = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const books = fs.readFileSync(require('node:path').join(__dirname, '..', 'books.js'), 'utf8');
const page = fs.readFileSync(require('node:path').join(__dirname, '..', 'index.html'), 'utf8');
const sql = fs.readFileSync(require('node:path').join(__dirname, '..', 'supabase/sql_25_trash.sql'), 'utf8');
const part = (source, from, to) => source.slice(source.indexOf(from), source.indexOf(to, source.indexOf(from)));

test('deleted books stay out of the shelf, including old assignments', () => {
  const ctx = { bkxLocal: () => [{id:'a',deletedAt:123},{id:'b'}], bkxGone: () => new Set(), bkAsgRecs: () => [{id:'a',asg:1},{id:'c',asg:1}], BKXBLOCK: new Set() };
  vm.runInNewContext(part(books, 'function bkxAll()', 'function bkxStore('), ctx);
  assert.deepEqual(Array.from(ctx.bkxAll(), b => b.id), ['b','c']);
});

test('newer deletion wins cross-device book merge', () => {
  const ctx = {};
  vm.runInNewContext(part(books, 'function bkxMerge(', 'async function bkxSync('), ctx);
  const result = ctx.bkxMerge([{id:'a',t:1}], [{id:'a',t:1,updatedAt:10,deletedAt:10}], new Set());
  assert.equal(result[0].deletedAt, 10);
});

test('QR access rejects local trash and server rejected IDs', async () => {
  const notices=[];
  const ctx = {bkBare:x=>x,bkxGone:()=>new Set(),bkxTrash:()=>[{id:'me-xb1'}],bkxAll:()=>[],toast:x=>notices.push(x),cloud:()=>true,rpc:async()=>({ok:true,json:async()=>false})};
  vm.runInNewContext(part(books, 'async function bkxAccess(', 'async function bkxCheckAssigned('), ctx);
  assert.equal(await ctx.bkxAccess('me-xb1'), false);
  ctx.bkxTrash=()=>[];
  assert.equal(await ctx.bkxAccess('me-xb1'), false);
  assert.ok(notices.length >= 2);
});

test('worksheet cloud metadata carries trash state', () => {
  const ctx = {};
  vm.runInNewContext(part(page, 'const wsMeta=', 'const wsPost='), ctx);
  assert.equal(vm.runInNewContext('wsMeta({deletedAt:123}).deletedAt', ctx), 123);
  assert.equal(vm.runInNewContext('wsMeta({}).deletedAt', ctx), null);
});

test('server functions block trashed QR resources and purge expired data', async (t) => {
  let PGlite;
  try { ({ PGlite } = require(process.env.PGLITE || '@electric-sql/pglite')); }
  catch (e) { t.skip('PGlite is not installed in this static checkout'); return; }
  const db = new PGlite();
  try {
    await db.exec(`create table students(id text primary key,name text);
      create table worksheets(id bigint generated always as identity, user_id text, student_id text, wid text, t bigint, title text, meta jsonb);
      create table attempts(user_id text, student_id text, t bigint, "set" text, sub text, items jsonb);
      create table teacher_settings(user_id text primary key,data jsonb,updated_at timestamptz default now());`);
    const localSql = sql.split('\n').filter(line => !/^(create extension|revoke all|grant execute|select cron\.schedule)/i.test(line.trim())).join('\n');
    await db.exec(localSql);
    await db.exec(`insert into worksheets(user_id,wid,t,title,meta) values
      ('u','ACTIVE01',1,'active','{}'),
      ('u','DELETED1',1,'deleted',jsonb_build_object('deletedAt',(extract(epoch from now())*1000)::bigint)),
      ('u','EXPIRED1',1,'expired',jsonb_build_object('deletedAt',(extract(epoch from now() - interval '31 days')*1000)::bigint));
      insert into teacher_settings(user_id,data) values ('u',jsonb_build_object('books',jsonb_build_array(
      jsonb_build_object('id','me-xb1'),jsonb_build_object('id','me-xb2','deletedAt',123))));
      insert into teacher_settings(user_id,data) values ('v',jsonb_build_object('books',jsonb_build_array(jsonb_build_object('id','me-xb2'))));`);
    assert.equal((await db.query("select public.ws_get('DELETED1') as v")).rows[0].v, null);
    assert.equal((await db.query("select public.ws_get('ACTIVE01') as v")).rows[0].v.title, 'active');
    assert.equal((await db.query("select public.book_access('me-xb1') as v")).rows[0].v, true);
    assert.equal((await db.query("select public.book_access('me-xb2') as v")).rows[0].v, false);
    assert.equal((await db.query("select public.book_access('me-xb2','v') as v")).rows[0].v, true);
    assert.equal((await db.query("select public.book_access('me-xb2','u') as v")).rows[0].v, false);
    await assert.rejects(db.query("select public.ws_submit('DELETED1', 2, '[]'::jsonb)"));
    await db.exec("update worksheets set meta=meta - 'deletedAt' where wid='DELETED1'");
    assert.equal((await db.query("select public.ws_get('DELETED1') as v")).rows[0].v.title, 'deleted');
    await db.exec("update teacher_settings set data=jsonb_set(data,'{books,1,deletedAt}','null'::jsonb) where user_id='u'");
    assert.equal((await db.query("select public.book_access('me-xb2','u') as v")).rows[0].v, true);
    await db.exec('select public.trash_purge()');
    assert.equal((await db.query("select count(*)::int as n from worksheets where wid='EXPIRED1'")).rows[0].n, 0);
  } finally { await db.close(); }
});
