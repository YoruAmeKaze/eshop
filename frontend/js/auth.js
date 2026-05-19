/* ============================================================
   auth.js — 登录 / 注册 / token 管理
   ============================================================ */

window.currentUser = null;

/* ---- token ---- */
function getToken() { return localStorage.getItem('kv_token'); }
function setToken(t) { localStorage.setItem('kv_token', t); }
function clearToken() { localStorage.removeItem('kv_token'); }

/* ---- 页面跳转 ---- */
window.showPage = function (id) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById(id).classList.add('active');
};

/* ---- 角色跳转 ---- */
function gotoHome(roles) {
  if (roles === 'consumer') {
    window.showPage('page-consumer');
    window.dispatchEvent(new Event('consumer:init'));
  } else if (roles === 'merchant') {
    window.showPage('page-merchant');
    window.dispatchEvent(new Event('merchant:init'));
  } else if (roles === 'admin') {
    window.showPage('page-admin');
    window.dispatchEvent(new Event('admin:init'));
  } else {
    clearToken();
    window.showPage('page-login');
  }
}

/* ---- 加载用户信息 ---- */
async function loadUser() {
  try {
    const data = await AuthAPI.getMe();
    if (data.status === 'success') {
      window.currentUser = data.data;
      return true;
    }
  } catch (e) { /* 401 已在 request() 里处理 */ }
  clearToken();
  window.showPage('page-login');
  return false;
}

/* ---- 登录 ---- */
async function doLogin() {
  const name = document.getElementById('login-name').value.trim();
  const password = document.getElementById('login-pass').value;
  const errEl = document.getElementById('login-error');
  errEl.classList.remove('show');

  if (!name || !password) {
    errEl.textContent = '请填写用户名和密码';
    errEl.classList.add('show');
    return;
  }
  try {
    const data = await AuthAPI.login(name, password);
    if (data.status === 'success') {
      setToken(data.token);
      const ok = await loadUser();
      if (ok) gotoHome(window.currentUser.roles);
    } else {
      errEl.textContent = data.message || '登录失败';
      errEl.classList.add('show');
    }
  } catch (e) {
    errEl.textContent = '无法连接服务器';
    errEl.classList.add('show');
  }
}

/* ---- 注册 ---- */
async function doRegister() {
  const name = document.getElementById('reg-name').value.trim();
  const password = document.getElementById('reg-pass').value;
  const tel = document.getElementById('reg-tel').value.trim();
  const roles = document.getElementById('reg-role').value;
  const errEl = document.getElementById('reg-error');
  const okEl = document.getElementById('reg-success');
  errEl.classList.remove('show');
  okEl.classList.remove('show');

  if (!name || !password) {
    errEl.textContent = '请填写用户名和密码';
    errEl.classList.add('show');
    return;
  }
  try {
    const data = await AuthAPI.register(name, password, roles, tel);
    if (data.status === 'success') {
      okEl.textContent = '注册成功！2秒后跳转登录...';
      okEl.classList.add('show');
      setTimeout(() => window.showPage('page-login'), 2000);
    } else {
      errEl.textContent = data.message || '注册失败';
      errEl.classList.add('show');
    }
  } catch (e) {
    errEl.textContent = '无法连接服务器';
    errEl.classList.add('show');
  }
}

/* ---- 退出登录 ---- */
window.doLogout = function () {
  clearToken();
  window.currentUser = null;
  document.getElementById('login-name').value = '';
  document.getElementById('login-pass').value = '';
  window.showPage('page-login');
};

/* ---- 渲染"我的"页（三个角色共用） ---- */
window.renderMe = function (containerId) {
  const u = window.currentUser;
  if (!u) return;
  const roleLabel = { consumer: '消费者', merchant: '商家', admin: '管理员' };
  const tagClass = { consumer: 'tag-consumer', merchant: 'tag-merchant', admin: 'tag-admin' };
  document.getElementById(containerId).innerHTML = `
    <div class="card" style="text-align:center;padding:28px 16px 20px;">
      <div class="avatar">${u.name.charAt(0).toUpperCase()}</div>
      <div style="font-size:20px;font-weight:700;color:#111;margin-bottom:8px;">${u.name}</div>
      <span class="tag ${tagClass[u.roles] || ''}">${roleLabel[u.roles] || u.roles}</span>
      ${u.tel ? `<div style="margin-top:10px;font-size:13px;color:#999;">📞 ${u.tel}</div>` : ''}
      <div style="font-size:12px;color:#ccc;margin-top:4px;">UID: ${u.id}</div>
    </div>
    <div class="card" style="padding:4px 16px;">
      <div class="menu-item">
        <span class="menu-icon">🔔</span><span class="menu-label">通知设置</span><span class="menu-arrow">›</span>
      </div>
      <div class="menu-item">
        <span class="menu-icon">🔒</span><span class="menu-label">账号安全</span><span class="menu-arrow">›</span>
      </div>
      <div class="menu-item">
        <span class="menu-icon">🙋</span><span class="menu-label">联系客服</span><span class="menu-arrow">›</span>
      </div>
      <div class="menu-item" style="border-bottom:none;" onclick="window.doLogout()">
        <span class="menu-icon">🚪</span>
        <span class="menu-label" style="color:#cf1322;">退出登录</span>
      </div>
    </div>
  `;
};

/* ---- Toast（全局，所有 JS 都可用） ---- */
window.showToast = function (msg) {
  const old = document.getElementById('kv-toast');
  if (old) old.remove();
  const el = document.createElement('div');
  el.id = 'kv-toast';
  el.className = 'kv-toast';
  el.textContent = msg;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 2200);
};

/* ---- 初始化 ---- */
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('login-pass')
    .addEventListener('keydown', e => { if (e.key === 'Enter') doLogin(); });

  (async () => {
    if (!getToken()) { window.showPage('page-login'); return; }
    const ok = await loadUser();
    if (ok) gotoHome(window.currentUser.roles);
  })();
});
