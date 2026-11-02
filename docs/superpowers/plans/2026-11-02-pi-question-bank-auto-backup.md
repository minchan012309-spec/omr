# Pi 문제은행 분리와 자동 백업 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** GitHub Pages 앱은 가볍게 유지하고, Pi SSD의 문제은행과 선생님 브라우저 데이터 자동 백업을 `bank.solvi.win`에서 안전하게 제공한다.

**Architecture:** `solvi.win`은 GitHub Pages 앱, `bank.solvi.win`은 Pi SSD의 JSON/JS와 인증 백업 API다. 문제은행용 Pi 배포물은 기존 CasaOS Nginx 앱과 분리된 `solvi-bank` Docker Compose 앱으로 제공한다. 앱의 데이터 URL은 한 상수에서 계산하고, Supabase access token을 검증한 뒤 `teacher_settings` 소유 행을 확인한 선생님만 자신의 gzip 백업 파일을 쓸 수 있다. 기존 GitHub Pages 앱은 외부 데이터 API 실패를 사용자에게 알리되 화면 전체를 멈추지 않는다.

**Tech Stack:** 정적 GitHub Pages 앱, Vanilla JavaScript, Service Worker, Node.js 표준 라이브러리 HTTP API, Docker Compose, Nginx, Cloudflare Tunnel, Supabase Auth user endpoint.

**Spec:** `docs/superpowers/specs/2026-11-02-pi-question-bank-and-auto-backup-design.md`

## Global Constraints

- UI 문구는 한국어이고 기존 Pretendard·정적 앱 구조를 유지한다.
- 문제 데이터와 실제 학생 백업은 Git에 추가하지 않는다.
- Pi는 Cloudflare Tunnel만 사용하며 새 공유기 포트포워딩을 만들지 않는다.
- API는 Supabase access token 검증, `teacher_settings` 소유 확인, 사용자 ID별 경로 분리, 파일 크기 제한, 변경 감지, 24시간 세밀 보관 + 30일 일별 보관 + 256MB 계정별 상한을 적용한다.
- `bank.solvi.win` 응답은 최종적으로 `https://solvi.win`만 CORS 허용한다. DNS 전환 검증 중에는 기존 `https://solvi.p-e.kr`를 임시 허용한다.
- 배포 파일을 바꾸면 `sw.js`의 `VER`과 HTML 참조 버전을 갱신한다.
- 기존 수동 JSON 내려받기·불러오기 기능은 유지한다.

## Review Focus

- Pi가 꺼지거나 Tunnel이 끊겼을 때 외부 문제은행 요청 실패가 앱 초기화를 멈추지 않고 명확한 안내만 남긴다.
- `bank/data.js` 외부 일반 스크립트가 앱 코드보다 먼저 로드되고, 로컬 개발·테스트에서는 상대 경로로 대체된다.
- 다른 Supabase 사용자 토큰으로 지정한 경로·파일명을 사용해 백업을 읽거나 덮어쓸 수 없다.
- 자동 백업 실패가 `omr_lastbk`를 갱신하지 않아 수동 백업 안내가 사라지지 않는다.
- 15분 주기 중복 실행과 탭 여러 개가 동시에 열릴 때 최신 성공 파일만 보관 정책에 반영된다.

---

### Task 1: 외부 문제은행 URL과 초기 데이터 로더

**Files:**
- Create: `bank-origin.js`
- Modify: `index.html:62, 125-153, 2783, 3789-3795`
- Modify: `sw.js:1-24`
- Create: `tests/question-bank-origin.test.cjs`

**Interfaces:**
- Produces: `window.SOLVI_BANK_ORIGIN` and `bankUrl(relativePath)` returning either a same-origin relative URL in local development or `https://bank.solvi.win/<relativePath>` in production.
- Consumes: existing `DIRS`, `loadBankIndex()`, `ensureTags()`, `conceptLoad()`, `offUrls()` data-loading call sites.

- [ ] **Step 1: Write failing origin-resolution and static load-order contracts**

Assert production host resolves `bank/data.js` and all four subject directories to the Pi hostname, localhost remains relative, and `bank-origin.js` runs before the external `bank/data.js` script.

- [ ] **Step 2: Run the new test and verify it fails**

Run: `node --test tests/question-bank-origin.test.cjs`
Expected: FAIL because the origin helper and its load ordering do not exist.

- [ ] **Step 3: Implement the origin helper and replace relative bank-resource requests**

Add a tiny early script that exposes the resolved origin and synchronously loads the initial `bank/data.js`; use `bankUrl()` only for bank folders, retaining relative URLs for app assets and local test use. Preserve current question de-duplication and lazy-loading behavior.

- [ ] **Step 4: Extend offline data collection for CORS-enabled Pi files**

Keep the app shell same-origin-only. Make `offUrls()` return resolved bank URLs and cache their successful CORS responses explicitly, without causing an external origin to be intercepted by the service worker fetch handler.

- [ ] **Step 5: Verify origin and static contracts**

Run: `node --test tests/question-bank-origin.test.cjs && node scripts/verify-static.cjs`
Expected: PASS.

### Task 2: Pi 정적 문제은행과 백업 API 배포물

**Files:**
- Create: `pi/question-bank/docker-compose.yml`
- Create: `pi/question-bank/.env.example`
- Create: `pi/question-bank/nginx.conf`
- Create: `pi/question-bank/backup-api/package.json`
- Create: `pi/question-bank/backup-api/server.mjs`
- Create: `pi/question-bank/backup-api/Dockerfile`
- Create: `tests/pi-backup-api.test.mjs`
- Modify: `pi/README.md`

**Interfaces:**
- Produces: `POST /api/backups` accepting JSON `{ payload, createdAt, digest }` and `Authorization: Bearer <Supabase access token>`; returns `{ savedAt, skipped }` only after durable gzip write or a matching-content check.
- Consumes: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `QUESTION_BANK_ROOT`, `BACKUP_ROOT`, `ALLOWED_ORIGIN`, and static data mount configured outside Git.
- Produces: static data at `/bank`, `/cm`, `/ph`, `/hl` and CORS headers for `https://solvi.win`.

- [ ] **Step 1: Write failing API tests with a stub token verifier and temporary backup root**

Cover valid teacher upload, missing/invalid token rejection, a verified user without a `teacher_settings` row rejection, payload size rejection, user-controlled traversal attempt rejection, gzip content, matching-content skip, and tiered age/size pruning.

- [ ] **Step 2: Run the API tests and verify they fail**

Run: `node --test tests/pi-backup-api.test.mjs`
Expected: FAIL because the backup API does not exist.

- [ ] **Step 3: Implement the dependency-light backup API**

Use Node standard-library HTTP, filesystem, crypto, zlib, and fetch. Verify bearer tokens through Supabase Auth; query `teacher_settings` with the verified user ID to establish teacher ownership; generate paths from server-verified user IDs only; write gzip snapshots atomically; and prune only dated backup files in that user's directory according to the retention policy.

- [ ] **Step 4: Add Nginx and Compose configuration for CasaOS**

Serve the SSD data directory read-only, proxy `/api/backups` to the API container, apply exact CORS headers, enforce a request body limit, expose a dedicated host port (not the existing CasaOS Nginx port), and document CasaOS import, SSD volume paths, and Cloudflare route `http://localhost:<solvi-bank port>`.

- [ ] **Step 5: Run API test suite and configuration validation**

Run: `node --test tests/pi-backup-api.test.mjs && docker compose -f pi/question-bank/docker-compose.yml config`
Expected: PASS and valid Compose configuration.

### Task 3: 선생님 자동 JSON 백업 클라이언트

**Files:**
- Modify: `index.html:160-190, 2160, 2199, 3846-3847`
- Create: `tests/teacher-auto-backup.test.cjs`

**Interfaces:**
- Consumes: `window.SOLVI_BANK_ORIGIN`, `sess.access_token`, `teacher()`, and local `omr_` keys.
- Produces: `autoBackupNow(reason)` and a timer that runs after teacher session initialization and once every 15 minutes; returns structured success/failure state without throwing into rendering.

- [ ] **Step 1: Write failing browser contracts for backup eligibility and payload selection**

Assert only authenticated teachers with a server-confirmed teacher setting schedule uploads; students/parents do not; `LSS` is excluded; unchanged payloads skip transfer; a successful upload updates `omr_lastbk`; and a failed upload preserves it and exposes an actionable Korean status.

- [ ] **Step 2: Run the auto-backup contract test and verify it fails**

Run: `node --test tests/teacher-auto-backup.test.cjs`
Expected: FAIL because no upload client or timer exists.

- [ ] **Step 3: Implement upload, retry, and reminder integration**

Use the resolved Pi origin for `/api/backups`, send the current access token, calculate a digest, debounce concurrent requests, schedule only after teacher authentication completes, and retain download-based `backupAll()`/`restoreAll()` unchanged. Update the existing banner text to identify the latest automatic Pi backup and preserve it after upload failure.

- [ ] **Step 4: Verify client contracts and static parsing**

Run: `node --test tests/teacher-auto-backup.test.cjs && node scripts/verify-static.cjs`
Expected: PASS.

### Task 4: 배포 절차·회귀·안전한 Git 데이터 분리 준비

**Files:**
- Create: `tools/deploy-question-bank.sh`
- Create: `docs/verification/pi-question-bank.md`
- Modify: `README.md`
- Modify: `sw.js`
- Modify: `WORKLOG.md`

**Interfaces:**
- Consumes: approved SSH/CasaOS destination path and the four source data directories.
- Produces: an explicit deploy command that copies only problem-bank data to the Pi and verifies remote index files before reporting success.

- [ ] **Step 1: Add a dry-run deploy contract**

Make the deploy script refuse an empty destination, list exactly the four data directories, and support a no-write dry-run verification path.

- [ ] **Step 2: Run it against a temporary local destination and verify expected copy set**

Run: `tools/deploy-question-bank.sh --dry-run --destination <temporary directory>`
Expected: no writes and a complete list of bank, cm, ph, and hl transfer roots.

- [ ] **Step 3: Implement the documented deployment and recovery workflow**

Use `rsync` with explicit sources, never delete the destination unless a separately documented opt-in flag is passed, and document the CasaOS static-data mount, automatic backup environment variables, `bank.solvi.win` Tunnel route, staged `solvi.win` GitHub Pages DNS switch, certificate readiness, manual rollback, and the separate approval required before removing data blobs from Git history.

- [ ] **Step 4: Update service worker version and run targeted verification**

Run: `node --test tests/question-bank-origin.test.cjs tests/pi-backup-api.test.mjs tests/teacher-auto-backup.test.cjs && node scripts/verify-static.cjs`
Expected: PASS.

- [ ] **Step 5: Run full regression appropriate to the final change**

Run: `npm test`
Expected: PASS all isolated verification commands.

## Self-review

- Spec coverage: Tasks 1-2 cover Pi data origin and secure API; Task 3 covers automatic teacher backup; Task 4 covers deployment, rollback, documentation, service worker version, and validation.
- Review focus coverage: Tasks 1 and 3 cover origin outage and local/production loading; Task 2 covers path isolation and retention; Task 3 covers failed uploads and duplicate timers.
- Deliberate deferral: Git history rewrite is excluded because it changes shared history and needs a separate user-approved migration after the new flow has operated successfully.
