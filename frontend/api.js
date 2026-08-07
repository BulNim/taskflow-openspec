// 공통 API 클라이언트 - JWT 자동 첨부, 401 시 자동 재로그인 유도
// 로컬 개발에서는 백엔드(8000)를 명시하고, 배포 환경에서는 같은 오리진(vercel.json 라우팅)을 사용한다.
window.API_BASE = window.API_BASE || (location.hostname === "localhost" || location.hostname === "127.0.0.1"
  ? "http://127.0.0.1:8000"
  : "");

// JWT를 localStorage에 저장/조회/삭제하는 헬퍼. 서버는 stateless이므로
// 로그아웃은 이 토큰을 지우는 것만으로 완료된다.
window.Auth = {
  getToken: () => localStorage.getItem("token"),
  setToken: (t) => localStorage.setItem("token", t),
  clear: () => localStorage.removeItem("token"),
};

// 모든 화면이 공통으로 쓰는 fetch 래퍼. 토큰이 있으면 Authorization 헤더를
// 자동으로 붙이고, 표준 에러 응답({ error: { code, message } })을 파싱해
// err.code / err.status로 던져서 각 화면이 케이스별 분기를 하기 쉽게 한다.
window.api = async function (path, { method = "GET", body } = {}) {
  const headers = { "Content-Type": "application/json" };
  const token = window.Auth.getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(window.API_BASE + path, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  // 토큰을 실어 보낸 요청이 401이면 세션 만료로 간주. 토큰 없이 보낸 로그인/회원가입
  // 요청의 401(예: 자격 증명 오류)은 아래 일반 에러 처리로 넘겨 실제 코드/메시지를 보존한다.
  if (res.status === 401 && token) {
    window.Auth.clear();
    if (!location.pathname.endsWith("login.html")) {
      location.href = "/login.html?expired=1";
    }
    throw new Error("TOKEN_EXPIRED");
  }

  // 204 No Content 등 바디가 없는 응답도 있으므로 파싱 실패는 조용히 무시한다.
  let data = null;
  try {
    data = await res.json();
  } catch (e) {
    data = null;
  }

  if (!res.ok) {
    const err = new Error(data?.error?.message || "요청에 실패했습니다");
    err.code = data?.error?.code;
    err.status = res.status;
    err.meta = data?.error?.meta;
    throw err;
  }
  return data;
};

// 각 화면 진입 시 호출하는 공통 라우팅 가드.
// requireAuth: 로그인 안 되어 있으면 /login.html로.
// requireTeam=true: 팀 미소속이면 /team.html로 (칸반/채팅 화면에서 사용).
// requireTeam=false: 이미 팀 소속이면 /kanban.html로 (팀 선택 화면에서 사용).
window.routeGuard = async function ({ requireAuth = true, requireTeam = null } = {}) {
  const token = window.Auth.getToken();
  if (requireAuth && !token) {
    location.href = "/login.html";
    return null;
  }
  if (!token) return null;

  try {
    const me = await window.api("/auth/me");
    if (requireTeam === true && !me.team_id) {
      location.href = "/team.html";
      return null;
    }
    if (requireTeam === false && me.team_id) {
      location.href = "/kanban.html";
      return null;
    }
    return me;
  } catch (e) {
    return null;
  }
};
