/* 학습지 · 시험지 디자인 시안 (미리보기 전용 — 승인 전에는 제품 인쇄 엔진에 연결하지 않는다)
   시안마다 설정값만 다르고, 머리말 · 문항 번호 · 보기 · 선지 · 꼬리말 · 쪽 나누기는 아래 공통 렌더러가 그린다. */
(function(){
const E=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const CN='①②③④⑤';
const fr=(a,b)=>`<span class="fr"><i>${a}</i><i>${b}</i></span>`;
const FIG_VT=`<svg viewBox="0 0 220 120" class="fig" role="img" aria-label="속도-시간 그래프"><path d="M30 10V100H210" fill="none" stroke="currentColor" stroke-width="1.2"/><path d="M30 90L110 30L190 30" fill="none" stroke="currentColor" stroke-width="2"/><path d="M110 30V100M190 30V100" stroke="currentColor" stroke-dasharray="3 3" stroke-width=".8"/><text x="14" y="16" font-size="10">v</text><text x="200" y="114" font-size="10">t</text><text x="22" y="94" font-size="9">v₀</text><text x="104" y="112" font-size="9">t₁</text><text x="184" y="112" font-size="9">2t₁</text></svg>`;
const FIG_TBL=`<table class="dt"><thead><tr><th>실험</th><th>A의 질량(g)</th><th>B의 질량(g)</th><th>생성물(g)</th></tr></thead><tbody><tr><td>Ⅰ</td><td>2</td><td>16</td><td>18</td></tr><tr><td>Ⅱ</td><td>4</td><td>16</td><td>18</td></tr><tr><td>Ⅲ</td><td>6</td><td>48</td><td>54</td></tr></tbody></table>`;
/* 예시 문항 — 모두 직접 작성한 예시이며 실제 기출 원문이 아니다 */
const SAMPLE=[
 {psg:'[1～2] 다음 글을 읽고 물음에 답하시오.',body:['글을 읽는 사람은 문장을 하나씩 받아들이는 데 그치지 않고, 앞에서 읽은 내용과 지금 읽는 내용을 끊임없이 연결한다. 이처럼 독자가 글의 정보를 서로 관련지어 하나의 의미 구조로 만드는 과정을 통합적 이해라 한다.','통합적 이해가 잘 이루어지려면 독자는 글의 중심 화제를 먼저 파악하고, 세부 정보가 그 화제와 어떤 관계에 있는지 판단해야 한다. ㉠<u>세부 정보를 중심 화제에 비추어 재배열하는 일</u>은 처음에는 느리지만, 익숙해지면 긴 글에서도 흐름을 놓치지 않게 해 준다.','한편 배경지식이 풍부한 독자는 글에 드러나지 않은 정보를 스스로 채워 넣기도 한다. 그러나 이러한 추론이 글의 내용과 어긋나면 오히려 이해를 방해할 수 있으므로, 독자는 자신의 추론을 글의 근거에 비추어 점검해야 한다.']},
 {q:'윗글의 내용과 일치하지 <u>않는</u> 것은?',ch:['독자는 앞뒤 내용을 연결하며 글을 읽는다.','통합적 이해는 정보를 하나의 의미 구조로 만드는 과정이다.','중심 화제를 파악하는 일은 세부 정보 판단보다 먼저 이루어진다.','배경지식에 의한 추론은 항상 이해를 돕는다.','독자는 자신의 추론을 글의 근거로 점검해야 한다.']},
 {q:'㉠에 대한 설명으로 가장 적절한 것은?',pt:3,ch:['글의 흐름을 놓치지 않도록 돕는다.','배경지식이 없을 때만 필요하다.','짧은 글에서만 효과가 있다.','중심 화제를 정하기 전에 해야 한다.','추론을 대신하는 방법이다.']},
 {q:`그림은 직선 운동하는 물체의 속도 <i>v</i>를 시간 <i>t</i>에 따라 나타낸 것이다. 0부터 2<i>t</i><sub>1</sub>까지 물체의 이동 거리는? (단, <i>v</i><sub>0</sub>=2 m/s, <i>t</i><sub>1</sub>=4 s)`,fig:FIG_VT,ch:['16 m','20 m','24 m','28 m','32 m'],row:1},
 {q:`표는 A와 B가 반응하여 생성물이 만들어지는 실험 Ⅰ~Ⅲ의 결과이다. 이에 대한 설명으로 옳은 것만을 <보기>에서 있는 대로 고른 것은?`,fig:FIG_TBL,box:['ㄱ. 실험 Ⅰ에서 A는 모두 반응한다.','ㄴ. 반응 질량비는 A : B = 1 : 8이다.',`ㄷ. 실험 Ⅲ에서 남은 B의 질량은 ${fr('1','2')}×48 g보다 작다.`],ch:['ㄱ','ㄴ','ㄱ, ㄷ','ㄴ, ㄷ','ㄱ, ㄴ, ㄷ'],row:1,pt:3},
 {q:'다음은 세포 호흡에 대한 학생 A~C의 대화이다. 제시한 내용이 옳은 학생만을 있는 대로 고른 것은?',box:['A: 포도당이 분해되면서 방출된 에너지 일부가 ATP에 저장돼.','B: 세포 호흡 결과 이산화 탄소와 물이 생성돼.','C: ATP가 ADP로 분해될 때 에너지가 흡수돼.'],ch:['A','C','A, B','B, C','A, B, C'],row:1},
 {q:`2H<sub>2</sub>(<i>g</i>) + O<sub>2</sub>(<i>g</i>) → 2H<sub>2</sub>O(<i>l</i>) 반응에서 H<sub>2</sub> 4 g이 모두 반응할 때 생성되는 H<sub>2</sub>O의 질량은? (단, H, O의 원자량은 각각 1, 16이다.)`,ch:['18 g','27 g','36 g','45 g','54 g'],row:1},
 {q:`질량이 <i>m</i>인 물체에 크기가 <i>F</i>인 힘이 작용할 때 가속도의 크기는 <i>a</i> = ${fr('<i>F</i>','<i>m</i>')}이다. 질량이 2 kg인 물체에 6 N의 알짜힘이 작용할 때 가속도의 크기는?`,ch:['1 m/s²','2 m/s²','3 m/s²','4 m/s²','6 m/s²'],row:1},
 {q:'다음 중 이어진문장을 이루는 연결 어미가 쓰인 것은?',ch:['비가 와서 길이 미끄럽다.','동생이 읽은 책이 재미있다.','그는 조용히 웃었다.','하늘이 매우 푸르다.','나는 친구와 함께 갔다.']},
 {sv:1,q:'윗글을 바탕으로, 독자가 배경지식에 의한 추론을 점검해야 하는 까닭을 두 문장 이내로 서술하시오.',pt:5}
];
/* 시안 설정. head·num·ch·box·foot·qsep·memo 등은 공통 렌더러의 변형 이름이다 */
const T=[
 // 기본 학습지
 {id:'W01',cat:'기본 학습지',name:'클린 2단',head:'minimal',num:'bold',cols:2,rule:1,ac:'#2f7fd0',font:'sans',fs:13,lh:1.7,foot:'simple'},
 {id:'W02',cat:'기본 학습지',name:'번호 원형 1단',head:'tab',num:'circle',cols:1,ac:'#1f6f5c',font:'sans',fs:13.5,lh:1.75,ch:'row',qsep:'line',memo:'lines',foot:'brand'},
 {id:'W03',cat:'기본 학습지',name:'두 자리 번호',head:'publisher',num:'two',cols:2,rule:0,ac:'#334155',font:'sans',fs:12.8,lh:1.7,foot:'simple'},
 {id:'W04',cat:'기본 학습지',name:'카드 문항',head:'card',num:'pill',cols:2,ac:'#6741d9',font:'sans',fs:12.6,lh:1.65,qsep:'card',foot:'brand'},
 {id:'W05',cat:'기본 학습지',name:'풀이 공간 넉넉',head:'minimal',num:'square',cols:1,ac:'#0b7285',font:'sans',fs:13.5,lh:1.75,memo:'grid',qsep:'line',foot:'simple'},
 {id:'W06',cat:'기본 학습지',name:'숙제 확인형',head:'check',num:'plain',cols:2,rule:1,ac:'#c2410c',font:'sans',fs:12.8,lh:1.7,foot:'brand'},
 {id:'W07',cat:'기본 학습지',name:'점선 구분',head:'center',num:'under',cols:2,rule:1,dash:1,ac:'#1e3a8a',font:'sans',fs:12.8,lh:1.7,qsep:'dot',foot:'simple'},
 // 학교 지필평가
 {id:'S01',cat:'학교 지필평가',name:'지필평가 표준',head:'school',num:'plain',cols:2,rule:1,ac:'#111',font:'serif',fs:13,lh:1.7,foot:'school',gray:1},
 {id:'S02',cat:'학교 지필평가',name:'지필평가 요약표',head:'schoolTable',num:'plain',cols:2,rule:1,ac:'#111',font:'serif',fs:12.8,lh:1.65,foot:'school',gray:1},
 {id:'S03',cat:'학교 지필평가',name:'서술형 답란 포함',head:'school',num:'plain',cols:1,ac:'#111',font:'serif',fs:13.5,lh:1.75,memo:'box',foot:'school',gray:1},
 {id:'S04',cat:'학교 지필평가',name:'배점 오른쪽 정렬',head:'schoolLine',num:'plain',cols:2,rule:1,ac:'#222',font:'serif',fs:12.8,lh:1.7,ptRight:1,foot:'school',gray:1},
 {id:'S05',cat:'학교 지필평가',name:'단원평가',head:'unitTest',num:'square',cols:2,rule:1,ac:'#2f7fd0',font:'sans',fs:12.8,lh:1.7,foot:'school'},
 {id:'S06',cat:'학교 지필평가',name:'수행평가 기록지',head:'perf',num:'pill',cols:1,ac:'#2b8a3e',font:'sans',fs:13.5,lh:1.75,memo:'box',foot:'simple'},
 {id:'S07',cat:'학교 지필평가',name:'중간고사 대비',head:'schoolBand',num:'bold',cols:2,rule:1,ac:'#364fc7',font:'sans',fs:12.8,lh:1.7,foot:'school'},
 // 수능 · 평가원형
 {id:'K01',cat:'수능 · 평가원형',name:'평가원 국어형',head:'kice',num:'plain',cols:2,rule:1,ac:'#111',font:'serif',fs:13,lh:1.72,foot:'kice',gray:1,subj:'국어 영역',sess:'제1교시'},
 {id:'K02',cat:'수능 · 평가원형',name:'평가원 과탐형',head:'kice',num:'plain',cols:2,rule:1,ac:'#111',font:'serif',fs:12.6,lh:1.65,foot:'kice',gray:1,subj:'과학탐구 영역',sess:'제4교시',sub:'화학 Ⅰ'},
 {id:'K03',cat:'수능 · 평가원형',name:'표지 · 유의 사항',head:'kiceCover',num:'plain',cols:2,rule:1,ac:'#111',font:'serif',fs:12.6,lh:1.65,foot:'kice',gray:1,subj:'과학탐구 영역',sess:'제4교시'},
 {id:'K04',cat:'수능 · 평가원형',name:'학원 모의평가',head:'mock',num:'plain',cols:2,rule:1,ac:'#1d4ed8',font:'serif',fs:12.8,lh:1.68,foot:'kice',subj:'과학탐구 영역'},
 {id:'K05',cat:'수능 · 평가원형',name:'교육청 학력평가형',head:'kiceLine',num:'plain',cols:2,rule:1,ac:'#111',font:'serif',fs:12.8,lh:1.68,foot:'kice',gray:1,subj:'국어 영역',sess:'제1교시'},
 {id:'K06',cat:'수능 · 평가원형',name:'실전 회차 번호',head:'round',num:'plain',cols:2,rule:1,ac:'#b91c1c',font:'serif',fs:12.8,lh:1.68,foot:'kice',subj:'과학탐구 영역'},
 {id:'K07',cat:'수능 · 평가원형',name:'파이널 봉투형',head:'final',num:'bold',cols:2,rule:1,ac:'#0f172a',font:'mix',fs:12.8,lh:1.68,foot:'kice',subj:'국어 영역'},
 // 미니멀
 {id:'M01',cat:'미니멀',name:'헤어라인',head:'hair',num:'plain',cols:2,rule:0,ac:'#111',font:'sans',fs:12.6,lh:1.8,foot:'tiny',light:1},
 {id:'M02',cat:'미니멀',name:'큰 여백 1단',head:'hair',num:'two',cols:1,ac:'#111',font:'sans',fs:13.5,lh:1.85,foot:'tiny',margin:[64,84],light:1},
 {id:'M03',cat:'미니멀',name:'왼쪽 번호 열',head:'minimal',num:'hang',cols:1,ac:'#475569',font:'sans',fs:13.5,lh:1.75,foot:'tiny'},
 {id:'M04',cat:'미니멀',name:'모노 그레이',head:'mono',num:'square',cols:2,rule:1,ac:'#52525b',font:'sans',fs:12.6,lh:1.7,foot:'tiny',gray:1},
 {id:'M05',cat:'미니멀',name:'세리프 에디토리얼',head:'center',num:'plain',cols:2,rule:0,ac:'#111',font:'serif',fs:13,lh:1.8,foot:'tiny'},
 {id:'M06',cat:'미니멀',name:'Q 표기',head:'hair',num:'q',cols:2,rule:0,ac:'#2f7fd0',font:'sans',fs:12.6,lh:1.75,foot:'tiny'},
 {id:'M07',cat:'미니멀',name:'촘촘한 복습',head:'mono',num:'plain',cols:2,rule:1,ac:'#111',font:'sans',fs:11.6,lh:1.55,foot:'tiny',margin:[36,40],qgap:12},
 // 프리미엄 교재
 {id:'P01',cat:'프리미엄 교재',name:'단원 대형 숫자',head:'publisher',num:'bold',cols:2,rule:0,ac:'#2f7fd0',font:'mix',fs:12.8,lh:1.72,box:'fill',foot:'brand'},
 {id:'P02',cat:'프리미엄 교재',name:'개념 요약 + 문제',head:'concept',num:'two',cols:2,rule:1,ac:'#1f6f5c',font:'sans',fs:12.6,lh:1.7,box:'top',foot:'brand'},
 {id:'P03',cat:'프리미엄 교재',name:'난이도 표시',head:'tab',num:'level',cols:2,rule:1,ac:'#6741d9',font:'sans',fs:12.6,lh:1.7,box:'fill',foot:'brand'},
 {id:'P04',cat:'프리미엄 교재',name:'유형 라벨',head:'band',num:'pill',cols:2,rule:0,ac:'#0b7285',font:'sans',fs:12.6,lh:1.7,typeLabel:1,foot:'brand'},
 {id:'P05',cat:'프리미엄 교재',name:'클래식 교과서',head:'center',num:'circle',cols:1,ac:'#7c2d12',font:'serif',fs:13.5,lh:1.8,box:'corner',memo:'lines',foot:'simple'},
 {id:'P06',cat:'프리미엄 교재',name:'다크 머리 띠',head:'band',num:'square',cols:2,rule:1,ac:'#0f172a',font:'sans',fs:12.6,lh:1.7,box:'top',foot:'brand'},
 {id:'P07',cat:'프리미엄 교재',name:'목표 체크',head:'goal',num:'bold',cols:2,rule:1,ac:'#c2410c',font:'mix',fs:12.6,lh:1.7,box:'fill',foot:'brand'},
 // 과목별
 {id:'X01',cat:'과목별',name:'국어 지문 독해',head:'tab',num:'plain',cols:2,rule:1,ac:'#e67700',font:'serif',fs:13,lh:1.8,psg:'frame',foot:'simple'},
 {id:'X02',cat:'과목별',name:'국어 문법 판단',head:'minimal',num:'circle',cols:2,rule:0,ac:'#e67700',font:'sans',fs:12.8,lh:1.72,ox:1,foot:'brand'},
 {id:'X03',cat:'과목별',name:'과학 자료 해석',head:'concept',num:'square',cols:2,rule:1,ac:'#2f7fd0',font:'sans',fs:12.6,lh:1.68,box:'fill',figFrame:1,foot:'brand'},
 {id:'X04',cat:'과목별',name:'물리 공식 강조',head:'publisher',num:'two',cols:2,rule:1,ac:'#6741d9',font:'mix',fs:12.8,lh:1.75,formula:1,foot:'brand'},
 {id:'X05',cat:'과목별',name:'생명 탐구 기록',head:'perf',num:'pill',cols:1,ac:'#2b8a3e',font:'sans',fs:13.2,lh:1.75,memo:'lines',figFrame:1,foot:'simple'},
 {id:'X06',cat:'과목별',name:'오답 노트',head:'note',num:'square',cols:1,ac:'#c92a2a',font:'sans',fs:13,lh:1.7,memo:'split',foot:'simple'},
 {id:'X07',cat:'과목별',name:'OX 개념 점검',head:'check',num:'bold',cols:2,rule:1,ac:'#0b7285',font:'sans',fs:12.6,lh:1.7,ox:1,foot:'brand'},
 {id:'X08',cat:'과목별',name:'주간 테스트',head:'weekly',num:'plain',cols:2,rule:1,ac:'#2f7fd0',font:'sans',fs:12.6,lh:1.68,foot:'school'}
];
/* ---------- 공통 조각 ---------- */
const fld=(l,w)=>`<span class="fld"><em>${l}</em><i style="width:${w||70}px"></i></span>`;
const HEAD={
 minimal:t=>`<header class="h-min"><div><b>${t.title}</b><span>${t.unit}</span></div><div class="meta">${fld('반',34)}${fld('이름',80)}</div></header>`,
 hair:t=>`<header class="h-hair"><span>${t.unit}</span><b>${t.title}</b><span>${fld('이름',80)}</span></header>`,
 mono:t=>`<header class="h-mono"><b>${t.title}</b><span>${t.unit} · ${t.n}문항</span>${fld('이름',80)}${fld('점수',44)}</header>`,
 tab:t=>`<header class="h-tab"><span class="tb">${t.unit}</span><b>${t.title}</b><div class="meta">${fld('날짜',60)}${fld('이름',80)}</div></header>`,
 publisher:t=>`<header class="h-pub"><span class="big">03</span><div><small>${t.series}</small><b>${t.title}</b><span>${t.unit}</span></div><div class="meta">${fld('이름',80)}</div></header>`,
 card:t=>`<header class="h-card"><div><small>${t.series}</small><b>${t.title}</b></div><div class="stat"><span><em>문항</em>${t.n}</span><span><em>맞힌 수</em>&nbsp;</span><span><em>이름</em>&nbsp;</span></div></header>`,
 check:t=>`<header class="h-check"><b>${t.title}</b><div class="cb">${['풀이','채점','오답 정리','질문'].map(x=>`<span><i></i>${x}</span>`).join('')}</div><div class="meta">${fld('이름',80)}</div></header>`,
 center:t=>`<header class="h-center"><small>${t.series}</small><b>${t.title}</b><div class="meta">${fld('학번',60)}${fld('이름',80)}</div></header>`,
 band:t=>`<header class="h-band"><div class="bd"><small>${t.series}</small><b>${t.title}</b></div><div class="meta">${fld('이름',80)}${fld('날짜',60)}</div></header>`,
 concept:t=>`<header class="h-concept"><div class="ttl"><small>${t.unit}</small><b>${t.title}</b></div><div class="sum"><b>핵심 정리</b><p>통합적 이해 = 정보 연결 + 중심 화제 파악 · 화학 반응식의 계수비 = 몰수비 · <i>F</i> = <i>ma</i></p></div></header>`,
 goal:t=>`<header class="h-goal"><b>${t.title}</b><ol><li>지문의 중심 화제를 찾는다</li><li>자료에서 비율을 읽는다</li><li>공식을 상황에 적용한다</li></ol>${fld('이름',80)}</header>`,
 note:t=>`<header class="h-note"><b>오답 노트</b><div class="meta">${fld('날짜',60)}${fld('원래 점수',44)}${fld('다시 푼 점수',44)}</div></header>`,
 perf:t=>`<header class="h-perf"><b>${t.title}</b><table><tr><th>학번</th><td></td><th>이름</th><td></td><th>평가 요소</th><td>자료 해석 · 서술</td></tr></table></header>`,
 weekly:t=>`<header class="h-weekly"><span class="wk">WEEK<br><b>07</b></span><div><b>${t.title}</b><span>${t.unit}</span></div><div class="meta">${fld('반',34)}${fld('이름',80)}${fld('점수',44)}</div></header>`,
 school:t=>`<header class="h-school"><div class="l1">2026학년도 2학기 1차 지필평가</div><div class="l2">제( 2 )학년 ( ${t.course} )</div><table><tr><th>일시</th><td>2026년 10월 14일 2교시</td><th>총 문항수</th><td>${t.n}문항(100점)</td></tr><tr><th>선다형</th><td>${t.n-1}문항(80점)</td><th>서술형</th><td>1문항(20점)</td></tr></table><div class="ids">${['반','번호','이름'].map(x=>`<span><em>${x}</em><i></i></span>`).join('')}</div></header>`,
 schoolTable:t=>`<header class="h-school2"><table><tr><td rowspan="2" class="t"><small>2026학년도 2학기 1차 지필평가</small><b>${t.course}</b></td><th>학년</th><th>반</th><th>번호</th><th>이름</th></tr><tr><td>2</td><td></td><td></td><td></td></tr></table><p>· 선다형 문항은 1번부터 ${t.n-1}번까지입니다. 알맞은 답을 골라 OMR 카드에 ●로 표시하시오.</p></header>`,
 schoolLine:t=>`<header class="h-schl"><b>2026학년도 2학기 1차 지필평가 · ${t.course}</b><span>2학년 · ${t.n}문항</span><div class="ids">${['반','번호','이름'].map(x=>`<span><em>${x}</em><i></i></span>`).join('')}</div></header>`,
 schoolBand:t=>`<header class="h-sband"><div class="bd"><b>중간고사 대비 ${t.course}</b><span>2학년 2학기 · 범위 Ⅰ-1 ~ Ⅱ-2</span></div><div class="meta">${fld('반',34)}${fld('이름',80)}${fld('점수',44)}</div></header>`,
 unitTest:t=>`<header class="h-unit"><span class="tb">단원평가</span><b>${t.unit}</b><div class="meta">${fld('반',34)}${fld('번호',34)}${fld('이름',80)}<span class="score">/ 100</span></div></header>`,
 kice:t=>`<header class="h-kice"><div class="yr">2027학년도 대학수학능력시험 대비 문제지</div><div class="row"><span class="ss">${t.sess}</span><b>${t.subj}</b><span class="odd">홀수형</span></div>${t.sub?`<div class="sub">${t.sub}</div>`:''}<div class="ids"><span><em>성명</em><i></i></span><span><em>수험 번호</em><i class="nb">${'<u></u>'.repeat(8)}</i></span></div></header>`,
 kiceCover:t=>`<header class="h-kcov"><div class="row"><span class="ss">${t.sess}</span><b>${t.subj}</b></div><div class="yr">2027학년도 대학수학능력시험 대비 모의평가 문제지</div><ul><li>자신이 선택한 과목의 문제지인지 확인하시오.</li><li>문제지의 해당란에 성명과 수험 번호를 정확히 쓰시오.</li><li>문항에 따라 배점이 다릅니다. 3점 문항에는 점수가 표시되어 있습니다. 점수 표시가 없는 문항은 모두 2점입니다.</li></ul><div class="ids"><span><em>성명</em><i></i></span><span><em>수험 번호</em><i class="nb">${'<u></u>'.repeat(8)}</i></span></div></header>`,
 kiceLine:t=>`<header class="h-kline"><span class="ss">${t.sess}</span><div><small>2026학년도 11월 고2 전국연합학력평가 대비</small><b>${t.subj}</b></div><span class="odd">홀수형</span></header>`,
 mock:t=>`<header class="h-mock"><div class="rd"><b>3</b><small>회</small></div><div><small>Solvi 모의평가</small><b>${t.subj}</b><span>${t.course}</span></div><div class="ids"><span><em>성명</em><i></i></span><span><em>학원</em><i></i></span></div></header>`,
 round:t=>`<header class="h-round"><b>FINAL</b><span class="no">12</span><div><b>${t.subj}</b><span>${t.course} · 실전 회차</span></div>${fld('성명',80)}</header>`,
 final:t=>`<header class="h-final"><div class="top"><span>${t.subj}</span><span>2027 수능 파이널</span><span>홀수형</span></div><b>${t.title}</b></header>`
};
const FOOT={
 simple:(t,p,P)=>`<footer class="f-simple"><span>${t.title}</span><b>${p}</b></footer>`,
 brand:(t,p,P)=>`<footer class="f-brand"><span>Solvi</span><span>${t.unit}</span><b>${p} / ${P}</b></footer>`,
 tiny:(t,p,P)=>`<footer class="f-tiny">${p}</footer>`,
 school:(t,p,P)=>`<footer class="f-school"><div>2026학년도 2학기 1차 지필평가 제(2)학년 (${t.course})과 (${P})쪽 가운데 (${p})쪽</div><small>이 시험 문제의 저작권은 ○○고등학교에 있습니다. 무단 전재와 복제를 금합니다.</small></footer>`,
 kice:(t,p,P)=>`<footer class="f-kice"><b>${p}</b><small>이 문제지에 관한 저작권은 출제자에게 있습니다.</small></footer>`
};
const NUM={
 plain:n=>`<b class="n n-plain">${n}.</b>`,bold:n=>`<b class="n n-bold">${n}</b>`,circle:n=>`<b class="n n-circle">${n}</b>`,square:n=>`<b class="n n-square">${n}</b>`,
 pill:n=>`<b class="n n-pill">문제 ${String(n).padStart(2,'0')}</b>`,two:n=>`<b class="n n-two">${String(n).padStart(2,'0')}</b>`,under:n=>`<b class="n n-under">${n}</b>`,
 q:n=>`<b class="n n-q">Q${n}</b>`,hang:n=>`<b class="n n-hang">${String(n).padStart(2,'0')}</b>`,
 level:n=>`<b class="n n-level">${String(n).padStart(2,'0')}<i>${'●'.repeat(1+n%3)}${'○'.repeat(2-n%3)}</i></b>`
};
const TYPES=['내용 일치','어휘 · 지시','그래프 해석','자료 해석','보기 판단','양적 관계','공식 적용','문법 판단','서술형'];
function qHtml(t,q,n){
 if(q.psg)return `<div class="blk psg-h">${q.psg}</div>`;
 const pt=q.pt?`<span class="pt">[${q.pt}점]</span>`:'';
 const stem=`<div class="stem">${(NUM[t.num]||NUM.plain)(q.sv?'서술형 1':n)}<div class="qt">${t.typeLabel?`<span class="tl">${TYPES[(n-1)%TYPES.length]}</span>`:''}${q.q}${t.ptRight?'':' '+pt}</div>${t.ptRight?pt:''}</div>`;
 const fig=q.fig?`<div class="figw${t.figFrame?' framed':''}">${q.fig}</div>`:'';
 const box=q.box?`<div class="bx bx-${t.box||'line'}"><span class="bt">&lt;보 기&gt;</span>${q.box.map(x=>`<p>${x}</p>`).join('')}</div>`:'';
 let ch='';
 if(t.ox&&q.ch)ch=`<div class="ox">${q.ch.slice(0,3).map(x=>`<p><span>${x}</span><i>O</i><i>X</i></p>`).join('')}</div>`;
 else if(q.ch){const mode=t.ch||((q.row||q.ch.every(x=>x.replace(/<[^>]+>/g,'').length<8))?'row':'stack');ch=`<div class="ch ch-${mode}">${q.ch.map((x,i)=>`<span><i>${CN[i]}</i>${x}</span>`).join('')}</div>`}
 const memo=q.sv||t.memo==='box'?'<div class="memo memo-box"></div>':t.memo==='lines'?'<div class="memo memo-lines"></div>':t.memo==='grid'?'<div class="memo memo-grid"></div>':t.memo==='split'?'<div class="memo memo-split"><div><em>틀린 이유</em></div><div><em>다시 풀이</em></div></div>':'';
 return `<div class="blk q">${stem}${fig}${box}${ch}${memo}</div>`;
}
/* ---------- 쪽 나누기: 블록을 단에 차례로 넣고, 넘치면 다음 단 · 다음 쪽으로. 긴 지문은 문단 단위로 나눠 이어 간다 ---------- */
function build(t,host,opt){
 opt=opt||{};const meta={title:t.titleText||'통합적 이해와 자료 해석',unit:'Ⅰ. 독서와 탐구 · 1. 정보의 통합',series:'Solvi 학습지',n:SAMPLE.filter(q=>!q.psg).length,course:'통합과학',subj:t.subj||'과학탐구 영역',sess:t.sess||'제4교시',sub:t.sub};
 const blocks=[];let n=0;
 const src=opt.long?SAMPLE.concat(SAMPLE.slice(3,9)):SAMPLE;
 src.forEach(q=>{if(q.psg){blocks.push({h:qHtml(t,q)});blocks.push({psg:q.body})}else blocks.push({h:qHtml(t,q,q.sv?0:++n)})});
 host.innerHTML='';const pages=[];
 const mk=()=>{const pg=document.createElement('section');pg.className='pg';pg.innerHTML=(pages.length===0?HEAD[t.head](meta):'<div class="run">'+meta.subj+' · '+meta.title+'</div>')+`<div class="cols c${t.cols}${t.rule?' rule':''}${t.dash?' dash':''}">${'<div class="col"></div>'.repeat(t.cols)}</div><div class="ft"></div>`;host.appendChild(pg);pages.push(pg);return [...pg.querySelectorAll('.col')]};
 let cols=mk(),ci=0;
 const over=c=>c.scrollHeight>c.clientHeight+1;
 const next=()=>{ci++;if(ci>=cols.length){if(opt.max&&pages.length>=opt.max)return false;cols=mk();ci=0}return true};
 for(const b of blocks){
  if(b.psg){let paras=b.psg.slice(),guard=0;while(paras.length&&guard++<20){const c=cols[ci],box=document.createElement('div');box.className='blk psg psg-'+(t.psg||'line');c.appendChild(box);let k=0;
    for(;k<paras.length;k++){const p=document.createElement('p');p.innerHTML=paras[k];box.appendChild(p);if(over(c)){box.removeChild(p);break}}
    if(k===0){c.removeChild(box);if(!c.children.length){box.innerHTML='<p>'+paras.shift()+'</p>';c.appendChild(box)}if(!next())return pages}else{paras=paras.slice(k);if(paras.length){box.classList.add('cut');if(!next())return pages}}}
   continue}
  const el=document.createElement('div');el.innerHTML=b.h;const node=el.firstChild;cols[ci].appendChild(node);
  if(over(cols[ci])&&cols[ci].children.length>1){cols[ci].removeChild(node);if(!next())break;cols[ci].appendChild(node)}
 }
 pages.forEach((pg,i)=>{pg.querySelector('.ft').outerHTML=(FOOT[t.foot]||FOOT.simple)(meta,i+1,pages.length)});
 return pages;
}
function apply(t,el){
 el.className='doc f-'+t.font+(t.light?' light':'')+(t.gray?' gray-ac':'')+(t.formula?' formula':'')+' q-'+(t.qsep||'none');
 el.style.cssText=`--ac:${t.ac};--fs:${t.fs}px;--lh:${t.lh};--mt:${(t.margin||[44,52])[0]}px;--ms:${(t.margin||[44,52])[1]}px;--qg:${t.qgap||22}px`;
}
window.WT={T,build,apply};
})();
