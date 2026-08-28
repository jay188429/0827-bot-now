# Google OAuth 2.0 (Token 방식) 실행 가이드

이 문서는 `index.html`에 구현된 Google OAuth 2.0 클라이언트(Token 방식)를 로컬 환경에서 실행하고 테스트하기 위한 설치 및 실행 가이드입니다.

---

## 1. 사전 준비 사항 (Google Cloud Console 설정)
1. [Google Cloud Console](https://console.cloud.google.com/)에 접속하여 프로젝트를 생성하거나 선택합니다.
2. **API 및 서비스 > 사용자 인증 정보(Credentials)** 메뉴로 이동합니다.
3. **[사용자 인증 정보 만들기] > [OAuth 클라이언트 ID]**를 선택합니다.
4. 애플리케이션 유형으로 **[웹 애플리케이션]**을 선택합니다.
5. **승인된 자바스크립트 원본(Authorized JavaScript origins)**에 다음 주소를 추가합니다 (로컬 개발 환경 기준):
   - `http://localhost:3000` (또는 사용하는 로컬 서버 주소)
6. 발급된 **클라이언트 ID**(`xxxx.apps.googleusercontent.com`)를 복사하여 `index.html` 파일 내의 `YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com` 부분에 입력합니다.

---

## 2. 패키지 설치 및 실행 방법

이 프로젝트는 순수 프론트엔드(HTML/JS)로 구성되어 있어 별도의 복잡한 백엔드 패키지는 필요하지 않습니다. 하지만 브라우저의 보안 정책(CORS)으로 인해 `file://` 프로토콜로는 Google OAuth가 정상 동작하지 않으므로, **로컬 웹 서버**를 통해 실행해야 합니다.

가장 간편한 방법 중 하나인 Node.js 기반의 `serve` 패키지를 사용하는 방법은 다음과 같습니다.

# Google OAuth 2.0 (Token 방식) 실행 가이드

이 문서는 `index.html`에 구현된 Google OAuth 2.0 클라이언트(Token 방식)를 로컬 환경에서 실행하고 테스트하기 위한 설치 및 실행 가이드입니다.

---

## 1. 사전 준비 사항 (Google Cloud Console 설정)
1. [Google Cloud Console](https://console.cloud.google.com/)에 접속하여 프로젝트를 생성하거나 선택합니다.
2. **API 및 서비스 > 사용자 인증 정보(Credentials)** 메뉴로 이동합니다.
3. **[사용자 인증 정보 만들기] > [OAuth 클라이언트 ID]**를 선택합니다。
4. 애플리케이션 유형으로 **[웹 애플리케이션]**을 선택합니다。
5. **승인된 자바스크립트 원본(Authorized JavaScript origins)**에 다음 주소를 추가합니다 (로컬 개발 환경 기준):
   - `http://localhost:3000` (또는 사용하는 로컬 서버 주소)
6. 발급된 **클라이언트 ID**(`xxxx.apps.googleusercontent.com`)를 복사하여 `index.html` 파일 내의 `YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com` 부분에 입력합니다.

---

## 2. 패키지 설치 및 실행 방법

이 프로젝트는 순수 프론트엔드(HTML/JS)로 구성되어 있어 별도의 복잡한 백엔드 패키지는 필요하지 않습니다. 하지만 브라우저의 보안 정책(CORS)으로 인해 `file://` 프로토콜로는 Google OAuth가 정상 동작하지 않으므로, **로컬 웹 서버**를 통해 실행해야 합니다.

### 방법 A: Node.js `serve` 사용 (추천)

1. **Node.js 설치 확인**
   터미널에서 Node.js와 npm이 설치되어 있는지 확인합니다:

1. **Node.js 설치 확인**
   터미널에서 Node.js와 npm이 설치되어 있는지 확인합니다:
   ```bash
   node -v
   npm -v
   ```

2. **로컬 서버 패키지 설치 (선택사항 - 글로벌 또는 npx 활용)**
   `npx`를 사용하면 별도의 설치 없이 바로 실행할 수 있습니다.
   ```bash
   npx serve . -l 3000
   ```
   *또는 프로젝트 내에 의존성으로 관리하고 싶다면:*
   ```bash
   npm init -y
   npm install serve --save-dev
   ```
   그리고 `package.json`의 `scripts`에 아래와 같이 추가합니다:
   ```json
   "scripts": {
     "start": "serve . -l 3000"
   }
   ```
   실행 명령어:
   ```bash
   npm start
   ```

3. **브라우저 접속**
   브라우저를 열고 `http://localhost:3000`으로 접속하여 구글 로그인 기능을 테스트합니다.

---

### 방법 B: Python 내장 서버 사용 (Node.js가 없는 경우)
만약 시스템에 Python이 설치되어 있다면, 아래 명령어로 간단히 서버를 실행할 수 있습니다.
```bash
python3 -m http.server 3000
```
그 후 브라우저에서 `http://localhost:3000` 접속

---

### 방법 C: VS Code Live Server Extension 사용
1. Visual Studio Code를 사용 중이라면 **Live Server** 확장 프로그램을 설치합니다.
2. `index.html` 파일을 우클릭한 뒤 **"Open with Live Server"**를 클릭합니다.
