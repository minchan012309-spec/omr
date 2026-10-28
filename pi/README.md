# 라즈베리파이 문제 데이터 서버

Solvi 앱이 문제 데이터(`bank/` `cm/` `ph/` `hl/` 폴더의 JSON)를 사이트 대신 라즈베리파이에서 받아 오게 하는 설정입니다.
공유기 포트포워딩은 필요 없습니다. 파이가 바깥으로 먼저 연결하는 방식(Tailscale Funnel)을 씁니다.

> 이 안내와 설치 스크립트는 라즈베리파이에서 직접 실행해 보지 못했습니다(앱 쪽 전환과 되돌리기만 시험했습니다). 막히면 오류 메시지를 그대로 알려 주세요.

## 동작 방식

```
학생·선생님 브라우저 ──https──▶ Tailscale Funnel ──▶ 파이(Caddy 파일 서버) ──▶ /srv/solvi/repo (GitHub에서 5분마다 자동 갱신)
        │
        └─ 파이가 응답하지 않으면 사이트 안 파일(bank/ cm/ ph/ hl/)로 자동 전환
```

- 앱(`index.html`)의 `DATA_ORIGIN_DEFAULT` 에 파이 주소를 적으면 켜집니다. 비워 두면 지금처럼 동작합니다.
- 파이에서 받은 문제는 기기에도 저장돼, 한 번 받은 뒤에는 인터넷이 없어도 열립니다.
- 파이가 두 번 연달아 응답하지 않으면 그 접속에서는 사이트 안 파일을 씁니다. **사이트 안 폴더를 지우기 전까지는** 파이가 꺼져도 서비스가 멈추지 않습니다.

## 준비물

- 라즈베리파이 4 이상(램 2GB 이상), 전원, **랜선 연결 권장**
- 저장장치: SD카드(32GB 이상). 오래 쓸 거라면 USB SSD를 권장합니다(SD카드는 쓰기가 많으면 고장이 납니다)
- 다른 컴퓨터(SD카드에 운영체제를 넣을 때 사용)

## 1. 운영체제 설치

1. 컴퓨터에 **Raspberry Pi Imager**(raspberrypi.com/software)를 설치합니다.
2. 운영체제는 `Raspberry Pi OS Lite (64-bit)` 를 고릅니다.
3. 톱니바퀴(설정)에서 호스트 이름 `solvi-data`, SSH 켜기, 사용자 이름·비밀번호, (무선이면) 와이파이를 설정한 뒤 SD카드에 씁니다.
4. 파이에 SD카드를 넣고 전원을 켭니다. 1~2분 뒤 컴퓨터에서 `ssh 사용자이름@solvi-data.local` 로 접속합니다.

## 2. 설치

파이에 접속한 상태에서 한 줄씩 실행합니다.

```bash
sudo apt-get install -y git
git clone --depth 1 https://github.com/minchan012309-spec/omr.git
sudo bash omr/pi/setup.sh
```

끝나면 확인합니다.

```bash
curl http://127.0.0.1:8080/health          # ok
curl -I http://127.0.0.1:8080/hl/index.json  # 200 이 나오면 성공
```

> 저장소가 비공개라면 3번째 줄이 실패합니다. 이 경우 GitHub에서 읽기 전용 토큰을 만들어 `REPO_URL=https://토큰@github.com/minchan012309-spec/omr.git sudo -E bash omr/pi/setup.sh` 로 실행하세요.

## 3. 밖에서 접속되게 하기 (Tailscale Funnel, 포트포워딩 없음)

1. 파이에서 `sudo tailscale up` 을 실행하고, 나오는 주소를 컴퓨터 브라우저에서 열어 Tailscale 계정(무료)으로 로그인합니다.
2. 브라우저에서 Tailscale 관리 화면(login.tailscale.com/admin)에 들어가 `DNS` 메뉴에서 **HTTPS Certificates** 를 켭니다.
3. 파이에서 실행합니다.

   ```bash
   sudo tailscale funnel --bg 8080
   tailscale funnel status
   ```

   처음에는 "Funnel 을 켜려면 이 주소를 여세요" 라는 링크가 나옵니다. 열어서 허용하면 됩니다.
4. 상태 화면에 `https://solvi-data.○○○.ts.net` 같은 주소가 나옵니다. 컴퓨터 브라우저(또는 스마트폰 데이터 연결)에서 `주소/health` 를 열어 `ok` 가 나오는지 확인합니다.

> Tailscale Funnel 은 무료로 쓸 수 있지만 전송량이 많으면 속도가 제한될 수 있습니다. 사용자가 늘어 느려지면 아래 "Cloudflare Tunnel" 로 바꾸세요(도메인이 필요합니다).

### 대안: Cloudflare Tunnel

도메인을 Cloudflare 에서 관리할 수 있다면 더 안정적입니다. Cloudflare 대시보드의 `Zero Trust → Networks → Tunnels` 에서 터널을 만들고, 안내에 나오는 `cloudflared` 설치 명령을 파이에 붙여넣은 뒤 `Public hostname` 을 `data.내도메인` → `http://127.0.0.1:8080` 으로 지정합니다.

## 4. 앱에 연결

`index.html` 에서 `DATA_ORIGIN_DEFAULT` 를 찾아 파이 주소를 적고 커밋·배포합니다. 끝에 `/` 는 붙이지 않습니다.

```js
const DATA_ORIGIN_DEFAULT='https://solvi-data.○○○.ts.net';
```

배포 후 앱에서 화법과 언어 교재를 열고, 브라우저 개발자도구(F12) → Network 에서 `hl/…json` 요청이 `ts.net` 주소로 가는지 확인합니다.
파이를 끄고 같은 화면을 다시 열어도 문제가 나오면(사이트 안 파일로 전환) 정상입니다.

시험용으로 컴퓨터에서 바로 바꿔 보려면(주소가 `localhost` 일 때만 동작):

```js
localStorage.setItem('omr_data_origin','https://solvi-data.○○○.ts.net'); location.reload();
// 되돌리기: localStorage.removeItem('omr_data_origin')
```

## 5. 사이트 용량을 실제로 줄이려면 (나중에, 파이가 안정된 뒤)

- 먼저 위 3~4번이 며칠 동안 문제없이 도는지 보세요. 파이가 꺼지면 사이트 안 폴더가 마지막 안전망입니다.
- 그다음 `bank/` `cm/` `ph/` `hl/` 의 큰 JSON 을 사이트 저장소에서 빼려면 데이터를 별도 저장소(예: `omr-data`)로 옮기고 `setup.sh` 의 `REPO_URL` 을 그쪽으로 바꿉니다. 이때 앱의 오프라인 저장·전범위 모의고사 같은 기능이 사이트 안 폴더를 가정하는 곳이 더 있는지 먼저 확인해야 합니다(현재는 `index.html` 의 4곳만 파이로 전환했습니다).

## 알아 둘 점

- **보안:** 앱은 받은 문제 HTML을 그대로 화면에 넣습니다. 파이가 해킹되면 모든 사용자 화면에 악성 코드가 들어갈 수 있으니, 파이 비밀번호는 길게 하고 SSH 는 키 로그인으로 바꾸고 `sudo apt-get update && sudo apt-get upgrade -y` 로 가끔 업데이트하세요. 앱은 정해진 주소(`https://…` 또는 `localhost`)만 받도록 막아 두었습니다.
- **API 키:** 문제 파일은 브라우저가 내려받는 공개 파일이라 키를 넣어도 보호가 되지 않습니다(키가 코드에 그대로 보이기 때문). 대신 `Caddyfile` 이 이 사이트에서 온 요청만 읽도록 허용합니다. 로그인한 사람에게만 문제를 주려면 별도 서버 코드(인증)가 필요합니다.
- **끊김:** 집·학교 인터넷이나 전기가 끊기면 파이에서 받는 문제는 멈춥니다(사이트 안 파일로 전환되는 동안은 괜찮습니다). 가능하면 UPS나 보조 전원, 유선 인터넷을 쓰세요.
- **속도:** 동시 접속이 많으면 파이의 업로드 속도가 병목이 됩니다. 앱이 한 번 받은 문제를 기기에 저장하므로 두 번째부터는 빠릅니다.
