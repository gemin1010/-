import sys
import os
import threading
import webbrowser
import http.server
import socketserver
import tempfile

HTML_CONTENT = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>학급 자리 뽑기</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Malgun Gothic','Apple SD Gothic Neo',sans-serif;background:#f5f5f5;color:#222;min-height:100vh;padding:16px}
.wrap{max-width:980px;margin:0 auto}
.toolbar{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:12px;align-items:center}
.toolbar button{padding:7px 16px;border:1px solid #ccc;background:#fff;color:#222;cursor:pointer;font-size:13px;font-weight:500;font-family:inherit}
.toolbar button:hover{background:#f0f0f0}
.toolbar button.primary{background:#2563eb;color:#fff;border-color:#2563eb}
.toolbar button.primary:hover{background:#1d4ed8}
.toolbar button.danger{background:#fef2f2;color:#b91c1c;border-color:#fca5a5}
.toolbar button.danger:hover{background:#fee2e2}
.sections{display:flex;gap:14px;align-items:flex-start}
.classroom-area{flex:1;min-width:0}
.side-panel{width:230px;flex-shrink:0}
.board{background:#fff;border:1px solid #ccc;padding:8px;text-align:center;font-weight:600;font-size:14px;color:#222;margin-bottom:12px}
.classroom-outer{position:relative;padding:0 34px}
.side-lbl{position:absolute;font-size:11px;color:#888;white-space:nowrap}
.lbl-window{left:0;top:50%;transform:translateY(-50%) rotate(-90deg)}
.lbl-corridor{right:0;top:50%;transform:translateY(-50%) rotate(90deg)}
.classroom{display:flex;justify-content:center;gap:20px}
.desk-group{display:flex;flex-direction:column;gap:6px}
.desk-block{display:grid;grid-template-columns:repeat(2,1fr);gap:6px}
.seat{width:66px;height:52px;border:1px solid #ccc;display:flex;flex-direction:column;align-items:center;justify-content:center;position:relative;background:#fff;cursor:pointer}
.seat:hover{opacity:0.82}
.seat.male{background:#f5f5f5;border-color:#f10f10f10}
.seat.female{background:#f5f5f5;border-color:#f10f10f10}
.seat.fixed-seat{border-style:dashed;border-width:2px}
.seat.empty-seat{background:#fafafa;border-color:#e5e7eb}
.seat.hidden-name .sname{visibility:hidden}
.sname{font-weight:600;font-size:12px;color:#222;max-width:60px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.badge{position:absolute;top:3px;right:4px;width:7px;height:7px}
.badge.male{background:#3b82f6}
.badge.female{background:#ec4899}
.seat-gender{position:absolute;bottom:3px;right:4px;font-size:9px;color:#aaa;cursor:pointer;line-height:1}
.seat-input{width:58px;font-size:12px;font-weight:600;border:none;outline:none;text-align:center;background:transparent;font-family:inherit;color:#222;padding:0}
.panel-section{background:#fff;border:1px solid #e5e7eb;padding:12px;margin-bottom:10px}
.panel-section h3{font-size:12px;font-weight:600;color:#555;margin-bottom:9px}
.student-list{max-height:160px;overflow-y:auto;margin-bottom:9px}
.student-item{display:flex;align-items:center;gap:5px;padding:4px 0;border-bottom:1px solid #f3f4f6;font-size:12px}
.student-item:last-child{border-bottom:none}
.fixed-item{display:flex;align-items:center;gap:4px;padding:3px 0;border-bottom:1px solid #f3f4f6;font-size:11px}
.fixed-item:last-child{border-bottom:none}
.stag{padding:1px 6px;font-size:10px;font-weight:600}
.stag.m{background:#dbeafe;color:#1d4ed8}
.stag.f{background:#fce7f3;color:#9d174d}
.empty-label{font-size:11px;color:#aaa;padding:3px 0}
.del{margin-left:auto;cursor:pointer;color:#bbb;border:none;background:none;font-family:inherit}
.del:hover{color:#ef4444}
.student-item .del{font-size:15px;line-height:1}
.fixed-item .del{font-size:14px}
.row-hint{color:#aaa;margin-left:4px}
.add-form{display:flex;flex-direction:column;gap:6px}
.add-form input,.add-form select{padding:6px 9px;border:1px solid #d1d5db;background:#fff;color:#222;font-size:12px;width:100%;font-family:inherit}
.add-form input:focus,.add-form select:focus{outline:2px solid #3b82f6;border-color:#3b82f6}
.add-form .row{display:flex;gap:6px}
.add-form .row input{flex:1}
.add-form button{padding:6px 10px;font-size:12px;border:1px solid #d1d5db;background:#f9fafb;color:#222;cursor:pointer;font-weight:500;font-family:inherit}
.add-form button:hover{background:#f3f4f6}
.fixed-list{max-height:100px;overflow-y:auto;margin-bottom:6px}
.msg{font-size:12px;padding:6px 10px;margin-bottom:10px}
.msg.ok{background:#f0fdf4;border:1px solid #86efac;color:#166534}
.msg.err{background:#fef2f2;border:1px solid #fca5a5;color:#b91c1c}
@media print{
  .toolbar,.side-panel,.msg{display:none!important}
  .sections{display:block}
  .classroom-area{width:100%}
  body{background:#fff;padding:0}
  .board{border:1px solid #333}
  .seat{border:1px solid #333!important;border-style:solid!important}
  .seat.male{background:#e8f0fe!important}
  .seat.female{background:#fce4ec!important}
}
</style>
</head>
<body>
<div class="wrap">
  <div class="toolbar">
    <button class="primary" onclick="doLottery()">▶ 자리 추첨</button>
    <button onclick="toggleNames()">이름 숨기기/보이기</button>
    <button onclick="window.print()">인쇄</button>
    <button onclick="saveData()">저장</button>
    <button onclick="loadData()">불러오기</button>
    <button class="danger" onclick="resetAll()">초기화</button>
  </div>
  <div id="msg-area"></div>
  <div class="sections">
    <div class="classroom-area">
      <div class="board">칠판</div>
      <div class="classroom-outer">
        <span class="side-lbl lbl-window">창가</span>
        <span class="side-lbl lbl-corridor">복도</span>
        <div class="classroom" id="classroom"></div>
      </div>
    </div>
    <div class="side-panel">
      <div class="panel-section">
        <h3>학생 목록 (<span id="count">0</span>명)</h3>
        <div class="student-list" id="student-list"></div>
        <div class="add-form">
          <div class="row">
            <input type="text" id="inp-name" placeholder="이름 또는 번호" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false">
            <select id="inp-gender"><option value="m">남</option><option value="f">여</option></select>
          </div>
          <button onclick="addStudent()">학생 추가</button>
        </div>
      </div>
      <div class="panel-section">
        <h3>자리 고정</h3>
        <div class="fixed-list" id="fixed-list"></div>
        <div class="add-form">
          <input type="text" id="inp-fix-name" placeholder="학생 이름/번호" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false">
          <select id="inp-fix-row">
            <option value="0">1행 (앞)</option>
            <option value="1">2행</option>
            <option value="2">3행</option>
            <option value="3">4행</option>
            <option value="4">5행 (뒤)</option>
          </select>
          <button onclick="addFixed()">고정 설정</button>
        </div>
      </div>
    </div>
  </div>
</div>
<input type="file" id="file-input" accept=".json" style="display:none" onchange="loadFile(event)">
<script>
const ROWS=5, COLS=6;
let students=[], fixedSeats=[], seats=mk(), showNames=true;

function mk(){return Array.from({length:ROWS},()=>Array(COLS).fill(null));}

const isHongmin=n=>n==='김홍민'||n==='7';
const isJaewon =n=>n==='이재원'||n==='19';
const isHyung  =n=>n==='김현겸'||n==='6';

function attachIME(el){
  let confirmed=el.value, composing='', active=false;
  const moveCursor=()=>{try{el.setSelectionRange(el.value.length,el.value.length);}catch(_){}};
  el.addEventListener('compositionstart',()=>{active=true;el.dataset.composing='1';confirmed=el.value;composing='';});
  el.addEventListener('compositionupdate',e=>{composing=e.data||'';el.value=confirmed+composing;moveCursor();});
  el.addEventListener('compositionend',e=>{
    const final=(e.data!=null&&e.data!=='')?e.data:composing;
    el.value=confirmed+final; confirmed=el.value; composing='';
    active=false; el.dataset.composing='0'; moveCursor();
  });
  el.addEventListener('input',()=>{if(!active)confirmed=el.value;});
}
attachIME(document.getElementById('inp-name'));
attachIME(document.getElementById('inp-fix-name'));

function addStudent(tries=0){
  const el=document.getElementById('inp-name');
  if(el.dataset.composing==='1'&&tries<30){requestAnimationFrame(()=>addStudent(tries+1));return;}
  const name=el.value.trim();
  if(!name)return showMsg('이름/번호를 입력하세요','err');
  if(students.some(s=>s.name===name))return showMsg('이미 추가된 학생입니다','err');
  students.push({name,gender:document.getElementById('inp-gender').value});
  el.value=''; el.focus();
  renderSidePanel(); showMsg(name+' 추가됨','ok');
}

function removeStudentByIndex(i){
  const {name}=students.splice(i,1)[0];
  fixedSeats=fixedSeats.filter(f=>f.name!==name);
  for(let r=0;r<ROWS;r++)for(let c=0;c<COLS;c++)if(seats[r][c]?.name===name)seats[r][c]=null;
  renderSidePanel(); renderClassroom();
}

function addFixed(tries=0){
  const el=document.getElementById('inp-fix-name');
  if(el.dataset.composing==='1'&&tries<30){requestAnimationFrame(()=>addFixed(tries+1));return;}
  const name=el.value.trim();
  const row=+document.getElementById('inp-fix-row').value;
  if(!name)return showMsg('이름/번호를 입력하세요','err');
  if(!students.some(s=>s.name===name))return showMsg('학생 목록에 없는 학생입니다','err');
  if(fixedSeats.some(f=>f.name===name))return showMsg('이미 고정된 학생입니다','err');
  fixedSeats.push({name,row});
  el.value='';
  renderSidePanel(); showMsg(name+' 고정됨','ok');
}

function removeFixedByIndex(i){fixedSeats.splice(i,1);renderSidePanel();}

function makeDelBtn(onclick){
  const btn=document.createElement('button');
  btn.className='del'; btn.textContent='×'; btn.onclick=onclick;
  return btn;
}

function renderSidePanel(){
  document.getElementById('count').textContent=students.length;
  const sl=document.getElementById('student-list');
  sl.innerHTML='';
  if(students.length){
    students.forEach((s,i)=>{
      const div=document.createElement('div');
      div.className='student-item';
      div.innerHTML=`<span class="stag ${s.gender}">${s.gender==='m'?'남':'여'}</span><span>${s.name}</span>`;
      div.appendChild(makeDelBtn(()=>removeStudentByIndex(i)));
      sl.appendChild(div);
    });
  } else {
    sl.innerHTML='<div class="empty-label">학생 없음</div>';
  }
  const fl=document.getElementById('fixed-list');
  fl.innerHTML='';
  if(fixedSeats.length){
    fixedSeats.forEach((f,i)=>{
      const div=document.createElement('div');
      div.className='fixed-item';
      div.innerHTML=`<span>${f.name}</span><span class="row-hint">→ ${f.row+1}행</span>`;
      div.appendChild(makeDelBtn(()=>removeFixedByIndex(i)));
      fl.appendChild(div);
    });
  } else {
    fl.innerHTML='<div class="empty-label">없음</div>';
  }
}

function renderClassroom(){
  const el=document.getElementById('classroom');
  el.innerHTML='';
  for(let b=0;b<3;b++){
    const group=document.createElement('div');
    group.className='desk-group';
    for(let r=0;r<ROWS;r++){
      const block=document.createElement('div');
      block.className='desk-block';
      for(let ci=0;ci<2;ci++) block.appendChild(makeSeatEl(r,b*2+ci));
      group.appendChild(block);
    }
    el.appendChild(group);
  }
}

function makeSeatEl(r,c){
  const stu=seats[r][c];
  const isFixed=stu&&fixedSeats.some(f=>f.name===stu.name&&f.row===r);
  const div=document.createElement('div');
  const cls=['seat'];
  if(stu)  cls.push(stu.gender==='m'?'male':'female');
  else     cls.push('empty-seat');
  if(isFixed)         cls.push('fixed-seat');
  if(stu&&!showNames) cls.push('hidden-name');
  div.className=cls.join(' ');
  if(stu){
    div.innerHTML=`<div class="badge ${stu.gender}"></div><div class="sname">${stu.name}</div>`;
    const gBtn=document.createElement('span');
    gBtn.className='seat-gender';
    gBtn.textContent=stu.gender==='m'?'':'';
    gBtn.onclick=e=>{
      e.stopPropagation();
      stu.gender=stu.gender==='m'?'f':'m';
      const s=students.find(s=>s.name===stu.name);
      if(s) s.gender=stu.gender;
      renderClassroom(); renderSidePanel();
    };
    div.appendChild(gBtn);
  }
  div.onclick=()=>openSeatEditor(r,c,div);
  return div;
}

function openSeatEditor(r,c,div){
  if(div.querySelector('.seat-input'))return;
  const stu=seats[r][c];
  div.innerHTML='';
  div.className='seat';
  const inp=document.createElement('input');
  inp.className='seat-input';
  inp.type='text';
  inp.value=stu?stu.name:'';
  inp.placeholder='이름';
  inp.autocomplete='off'; inp.autocorrect='off';
  inp.autocapitalize='off'; inp.spellcheck=false;
  inp.maxLength=10;
  attachIME(inp);
  function commit(){
    const name=inp.value.trim();
    const oldName=stu?.name||null;
    if(!name){
      seats[r][c]=null;
    } else if(name!==oldName){
      for(let rr=0;rr<ROWS;rr++)
        for(let cc=0;cc<COLS;cc++)
          if(seats[rr][cc]?.name===name&&!(rr===r&&cc===c)) seats[rr][cc]=null;
      if(!students.some(s=>s.name===name)){
        const gender=stu?.gender||'m';
        students.push({name,gender});
      }
      const gender=students.find(s=>s.name===name)?.gender||'m';
      seats[r][c]={name,gender};
    }
    renderClassroom(); renderSidePanel();
  }
  inp.addEventListener('keydown',e=>{
    if(e.key==='Enter'&&inp.dataset.composing!=='1') commit();
    if(e.key==='Escape') renderClassroom();
  });
  inp.addEventListener('blur',()=>setTimeout(commit,120));
  div.appendChild(inp);
  div.onclick=e=>e.stopPropagation();
  setTimeout(()=>{inp.focus();inp.select();},0);
}

function toggleNames(){showNames=!showNames;renderClassroom();}

function doLottery(){
  if(!students.length)return showMsg('학생을 먼저 추가하세요','err');
  if(students.length>ROWS*COLS)return showMsg(`학생 수(${students.length}명)가 자리 수(${ROWS*COLS}개)를 초과합니다`,'err');
  for(let i=0;i<3000;i++){
    const r=tryArrange();
    if(r){seats=r;renderClassroom();showMsg('자리 배치 완료!','ok');return;}
  }
  showMsg('조건에 맞는 배치를 찾지 못했습니다. 조건을 확인해 주세요','err');
}

function tryArrange(){
  const grid=mk(), placed=new Set();
  const emptyCount=ROWS*COLS-students.length;
  const blocked=new Set();
  if(emptyCount>0&&emptyCount%2===0){
    let rem=emptyCount;
    for(let r=ROWS-1;r>=0&&rem>0;r--)
      for(let b=2;b>=0&&rem>0;b--){
        const k0=r*COLS+b*2, k1=k0+1;
        if(!blocked.has(k0)&&!blocked.has(k1)){blocked.add(k0);blocked.add(k1);rem-=2;}
      }
  }
  const isBlocked=(r,c)=>blocked.has(r*COLS+c);
  const hongmin=students.find(s=>isHongmin(s.name));
  let hPos=null;
  if(hongmin){
    for(const c of shuffled([...Array(COLS).keys()])){
      if(!grid[0][c]&&!isBlocked(0,c)){grid[0][c]=hongmin;placed.add(hongmin.name);hPos={r:0,c};break;}
    }
    if(!hPos)return null;
  }
  for(const fix of fixedSeats){
    if(placed.has(fix.name))continue;
    const stu=students.find(s=>s.name===fix.name);
    if(!stu)continue;
    let ok=false;
    for(const c of shuffled([...Array(COLS).keys()])){
      if(grid[fix.row][c]||isBlocked(fix.row,c)||!check(grid,stu,fix.row,c,hPos))continue;
      grid[fix.row][c]=stu; placed.add(stu.name); ok=true; break;
    }
    if(!ok)return null;
  }
  const unplaced=shuffled(students.filter(s=>!placed.has(s.name)));
  const empties=shuffled(allEmpty(grid).filter(([r,c])=>!isBlocked(r,c)));
  for(const stu of unplaced){
    let done=false;
    for(let i=0;i<empties.length;i++){
      const [r,c]=empties[i];
      if(grid[r][c]||!check(grid,stu,r,c,hPos))continue;
      grid[r][c]=stu; empties.splice(i,1); done=true; break;
    }
    if(!done)return null;
  }
  return grid;
}

function allEmpty(grid){
  const res=[];
  for(let r=0;r<ROWS;r++)for(let c=0;c<COLS;c++)if(!grid[r][c])res.push([r,c]);
  return res;
}

function check(grid,stu,r,c,hPos){
  if(isJaewon(stu.name)&&hPos&&r===hPos.r&&Math.abs(c-hPos.c)===1)return false;
  const partnerC=(c%2===0)?c+1:c-1;
  if(stu.gender==='f'){
    if(r+1<ROWS&&grid[r+1][c]&&isHyung(grid[r+1][c].name))return false;
    if(grid[r][partnerC]&&isHyung(grid[r][partnerC].name))return false;
  }
  if(isHyung(stu.name)){
    if(r-1>=0&&grid[r-1][c]&&grid[r-1][c].gender==='f')return false;
    if(grid[r][partnerC]&&grid[r][partnerC].gender==='f')return false;
  }
  return true;
}

function shuffled(arr){
  for(let i=arr.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[arr[i],arr[j]]=[arr[j],arr[i]];}
  return arr;
}

function saveData(){
  const data={students,fixedSeats,seats:seats.map(row=>row.map(s=>s?{name:s.name,gender:s.gender}:null))};
  const a=document.createElement('a');
  a.href=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));
  a.download='자리배치_'+new Date().toLocaleDateString('ko-KR').replace(/[\. ]/g,'')+'.json';
  a.click();
  showMsg('저장됐습니다','ok');
}

function loadData(){document.getElementById('file-input').click();}

function loadFile(e){
  const file=e.target.files[0];
  if(!file)return;
  const reader=new FileReader();
  reader.onload=ev=>{
    try{
      const d=JSON.parse(ev.target.result);
      students=d.students||[];
      fixedSeats=d.fixedSeats||[];
      seats=d.seats?d.seats.map(row=>row.map(s=>s||null)):mk();
      renderSidePanel(); renderClassroom();
      showMsg('불러오기 완료','ok');
    }catch{showMsg('파일을 읽을 수 없습니다','err');}
  };
  reader.readAsText(file);
  e.target.value='';
}

function resetAll(){
  if(!confirm('모든 데이터를 초기화할까요?'))return;
  students=[]; fixedSeats=[]; seats=mk();
  renderSidePanel(); renderClassroom(); showMsg('초기화됐습니다','ok');
}

function showMsg(text,type='ok'){
  document.getElementById('msg-area').innerHTML=`<div class="msg ${type}">${text}</div>`;
  setTimeout(()=>document.getElementById('msg-area').innerHTML='',3000);
}

students=[
  {name:'강채우',gender:'f'},{name:'김기헌',gender:'m'},
  {name:'김준환',gender:'m'},{name:'김민호',gender:'m'},
  {name:'김향이',gender:'f'},{name:'김현겸',gender:'m'},
  {name:'김홍민',gender:'m'},{name:'박다녕',gender:'f'},
  {name:'손윤지',gender:'f'},{name:'유소민',gender:'f'},
  {name:'유준원',gender:'m'},{name:'유현영',gender:'f'},
  {name:'윤수빈',gender:'f'},{name:'이가희',gender:'f'},
  {name:'이유진',gender:'f'},{name:'이병재',gender:'m'},
  {name:'이봉찬',gender:'m'},{name:'이민주',gender:'f'},
  {name:'이재원',gender:'f'},{name:'이채윤',gender:'f'},
  {name:'이하은',gender:'f'},{name:'장예주',gender:'f'},
  {name:'조효영',gender:'f'},{name:'최지효',gender:'f'},
  {name:'한도윤',gender:'m'},{name:'강혜원',gender:'f'}
];
renderSidePanel(); renderClassroom();
<\/script>
</body>
</html>"""

PORT = 0  # 0 = OS가 빈 포트 자동 선택

def find_free_port():
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def run_server(port, html_path):
    handler = http.server.SimpleHTTPRequestHandler
    os.chdir(os.path.dirname(html_path))
    with socketserver.TCPServer(("", port), handler) as httpd:
        httpd.serve_forever()

def main():
    # HTML을 임시 파일로 저장
    tmp_dir = tempfile.mkdtemp()
    html_path = os.path.join(tmp_dir, 'index.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(HTML_CONTENT)

    port = find_free_port()

    # 서버를 백그라운드 스레드로 실행
    t = threading.Thread(target=run_server, args=(port, html_path), daemon=True)
    t.start()

    # 브라우저 열기
    import time
    time.sleep(0.5)
    webbrowser.open(f'http://localhost:{port}/index.html')

    # 메인 스레드는 살아있어야 서버가 유지됨
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
