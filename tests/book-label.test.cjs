/* 최근 기록의 교재 이름: 자유 구성 교재 ID(xf…_…)가 그대로 나오지 않는다 */
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('fs');
const src=fs.readFileSync(__dirname+'/../index.html','utf8');
const fn=src.match(/function bookLbl[\s\S]*?\n return n\+\(pg==='all'\?' 전체':' p\.'\+pg\)}/)[0];
const ID='hl-xfq_xh0_xw30_xv30_xs0_xj0_r3.4.5.6.7.8.9.10_a1';
function make(books){global.localStorage={getItem:()=>JSON.stringify(books)};global.bkxAll=undefined;return eval('('+fn+')')}
test('자유 구성 교재는 만든 이름과 쪽 번호로 보인다',()=>{assert.equal(make([{id:ID,name:'화법 출처별 문제집'}])(ID+':12'),'화법 출처별 문제집 p.12')});
test('이름을 모르면 「맞춤 교재」, ID는 보이지 않는다',()=>{const t=make([])(ID+':12');assert.equal(t,'맞춤 교재 p.12');assert.ok(!/xfq|_x/.test(t))});
test('기본 교재 · 전범위 모의고사 · 전체',()=>{const f=make([]);assert.equal(f('me-c:12'),'개념서 p.12');assert.equal(f('hl-hs:3'),'주교재 화법편 p.3');assert.equal(f('hl-xe20r3:all'),'전범위 모의고사 3회 전체');assert.equal(f('hl-xe20l7s1.2r4:5'),'전범위 모의고사 4회 p.5')});
