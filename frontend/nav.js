// 헤더 네비게이션 - 칸반/채팅/멤버 탭 공통 렌더. active: "kanban" | "chat" | "members"
window.renderNav = function (active, me) {
  const tabs = [
    { key: "kanban", label: "칸반", href: "kanban.html" },
    { key: "chat", label: "채팅", href: "chat.html" },
  ];

  const tabHtml = (t, mobile) => `
    <a href="${t.href}" class="${mobile ? "px-3 py-2.5 rounded-xl" : "px-3 py-1.5 rounded-lg"} text-sm font-bold ${
      t.key === active
        ? "bg-ink dark:bg-fg text-white dark:text-canvas"
        : "text-ink-2 dark:text-dim hover:bg-page dark:hover:bg-edge"
    } transition">${t.label}</a>`;

  document.getElementById("navSlot").innerHTML = `
    <header class="sticky top-0 z-30 bg-white dark:bg-canvas border-b border-line dark:border-edge">
      <div class="max-w-7xl mx-auto px-4 h-14 flex items-center gap-3">
        <button id="burger" class="md:hidden w-8 h-8 -ml-1 grid place-items-center rounded-lg hover:bg-page dark:hover:bg-edge" aria-label="메뉴">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M4 6h16M4 12h16M4 18h16"/></svg>
        </button>
        <div class="hidden md:flex items-center gap-2 shrink-0">
          <div class="w-7 h-7 rounded-lg bg-ink dark:bg-fg grid place-items-center text-white dark:text-canvas font-extrabold text-sm">T</div>
          <span class="font-extrabold tracking-tight">TaskFlow</span>
        </div>
        <button id="teamMembersBtn" class="hidden md:flex items-center gap-1.5 text-sm font-semibold hover:text-blue-text dark:hover:text-blue-dot transition">
          팀 멤버
        </button>
        <nav class="hidden md:flex items-center gap-1 ml-3">
          ${tabs.map((t) => tabHtml(t, false)).join("")}
        </nav>
        <div class="ml-auto flex items-center gap-2" id="themeSlot"></div>
        <span class="hidden lg:block text-sm text-ink-2 dark:text-dim">${me.email}</span>
        <button id="logoutBtnNav" class="hidden md:block text-sm font-bold text-ink-2 dark:text-dim hover:text-ink dark:hover:text-fg transition">로그아웃</button>
      </div>
    </header>

    <div id="menu" class="hidden fixed inset-0 z-50">
      <div class="absolute inset-0 bg-black/40" data-menu-close></div>
      <nav class="absolute left-0 top-0 bottom-0 w-64 bg-white dark:bg-surface p-4 flex flex-col gap-1">
        <div class="flex items-center gap-2 mb-4 px-1">
          <div class="w-7 h-7 rounded-lg bg-ink dark:bg-fg grid place-items-center text-white dark:text-canvas font-extrabold text-sm">T</div>
          <span class="font-extrabold">TaskFlow</span>
        </div>
        ${tabs.map((t) => tabHtml(t, true)).join("")}
        <button id="membersBtnMobile" class="px-3 py-2.5 rounded-xl text-sm font-semibold text-ink-2 dark:text-dim text-left">팀 멤버</button>
        <div class="mt-auto pt-4 border-t border-line dark:border-edge">
          <p class="px-3 text-[12px] text-ink-3 dark:text-dim">${me.email}</p>
          <button id="logoutBtnMobile" class="w-full mt-2 px-3 py-2.5 rounded-xl text-left text-sm font-bold text-red-text dark:text-red-dot">로그아웃</button>
        </div>
      </nav>
    </div>

    <div id="membersPanel" class="hidden fixed inset-0 z-50">
      <div class="absolute inset-0 bg-black/40" data-members-close></div>
      <div class="absolute right-0 top-0 bottom-0 w-80 max-w-[85vw] bg-white dark:bg-surface p-4 overflow-y-auto">
        <div class="flex items-center justify-between mb-3">
          <h2 class="text-sm font-extrabold">팀 멤버</h2>
          <button data-members-close class="w-7 h-7 grid place-items-center rounded-lg hover:bg-page dark:hover:bg-edge">✕</button>
        </div>
        <div id="inviteCodeBox" class="mb-4"></div>
        <div id="membersList" class="space-y-2"></div>
      </div>
    </div>
  `;

  document.getElementById("themeSlot").innerHTML = window.THEME_BTN;
  window.initTheme();

  // 모바일 햄버거 메뉴 열기/닫기 (< 768px에서만 보이는 버튼)
  const openMenu = () => document.getElementById("menu").classList.remove("hidden");
  const closeMenu = () => document.getElementById("menu").classList.add("hidden");
  document.getElementById("burger").onclick = openMenu;
  document.querySelectorAll("[data-menu-close]").forEach((el) => (el.onclick = closeMenu));

  // "팀 멤버" 패널 - 열 때마다 팀 정보(초대코드 재조회 포함)와 멤버 목록을 새로 불러온다.
  // 초대코드는 팀 생성 직후 한 번만 보여주지 않고 언제든 여기서 다시 확인할 수 있다.
  const openMembers = async () => {
    const panel = document.getElementById("membersPanel");
    panel.classList.remove("hidden");
    closeMenu();
    const [team, members] = await Promise.all([
      window.api(`/teams/${me.team_id}`),
      window.api(`/teams/${me.team_id}/members`),
    ]);
    document.getElementById("inviteCodeBox").innerHTML = `
      <p class="text-xs font-bold mb-1.5">초대 코드</p>
      <div class="flex items-center gap-2">
        <code class="flex-1 h-10 px-3 grid place-items-center rounded-lg bg-page dark:bg-chip font-mono text-sm font-bold tracking-widest">${team.invite_code}</code>
        <button id="copyInviteBtn" class="h-10 px-3 rounded-lg bg-white dark:bg-chip border border-line dark:border-edge text-xs font-bold">복사</button>
      </div>`;
    document.getElementById("copyInviteBtn").onclick = () => navigator.clipboard.writeText(team.invite_code);
    document.getElementById("membersList").innerHTML = members
      .map(
        (m) => `
        <div class="flex items-center gap-3 rounded-xl bg-white dark:bg-surface border border-line dark:border-edge px-3.5 py-2.5">
          <div class="w-7 h-7 rounded-full ${m.role === "owner" ? "bg-purple-dot" : "bg-blue-dot"} shrink-0"></div>
          <div class="min-w-0">
            <p class="text-[13px] font-bold truncate">${m.email}</p>
          </div>
          <span class="ml-auto shrink-0 px-2 py-0.5 rounded-md text-[10px] font-extrabold ${
            m.role === "owner" ? "bg-purple-dot text-white" : "bg-page dark:bg-chip text-ink-2 dark:text-dim"
          }">${m.role}</span>
        </div>`
      )
      .join("");
  };
  document.getElementById("teamMembersBtn").onclick = openMembers;
  document.getElementById("membersBtnMobile").onclick = openMembers;
  document.querySelectorAll("[data-members-close]").forEach((el) => (el.onclick = () => document.getElementById("membersPanel").classList.add("hidden")));

  // 서버에 로그아웃을 알린 뒤(실패해도 무시 - stateless라 서버 상태는 없음) 로컬 토큰을 지우고 로그인 화면으로.
  const doLogout = async () => {
    try {
      await window.api("/auth/logout", { method: "POST" });
    } catch (e) {}
    window.Auth.clear();
    location.href = "/login.html";
  };
  document.getElementById("logoutBtnNav").onclick = doLogout;
  document.getElementById("logoutBtnMobile").onclick = doLogout;
};
