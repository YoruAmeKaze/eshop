/* ============================================================
   api.js — 所有后端请求统一管理
   新增接口只需在这里添加函数，页面逻辑不用改
   ============================================================ */

const API_BASE = '';

// 通用请求函数
async function request(method, path, body = null, auth = false) {
  const headers = { 'Content-Type': 'application/json' };
  if (auth) {
    const token = localStorage.getItem('kv_token');
    // trim() 防止意外空格导致 401
    if (token) headers['Authorization'] = 'Bearer ' + token.trim();
  }
  const options = { method, headers };
  if (body) options.body = JSON.stringify(body);

  const res = await fetch(API_BASE + path, options);
  if (res.status === 401) {
    localStorage.removeItem('kv_token');
    window.showPage('page-login');
    throw new Error('登录已过期，请重新登录');
  }
  return res.json();
}

/* ============================================================
   Auth（已完成）
   ============================================================ */
const AuthAPI = {
  login(name, password) {
    return request('POST', '/api/login', { name, password });
  },
  register(name, password, roles, tel) {
    const body = { name, password, roles };
    if (tel) body.tel = tel;
    return request('POST', '/api/register', body);
  },
  getMe() {
    return request('GET', '/api/user/me', null, true);
  },
};

/* ============================================================
   商品
   ============================================================ */
const ProductAPI = {
  async getList(page = 1, limit = 10, category = null) {
    let url = `/api/products?page=${page}&limit=${limit}`;
    if (category) url += `&category=${encodeURIComponent(category)}`;
    return request('GET', url);
  },

  async getDetail(id) {
    return request('GET', `/api/products/${id}`);
  },

  // 商家：自己店铺的商品
  async getMerchantProducts() {
    return request('GET', '/api/merchant/products', null, true);
  },

  async create(data) {
    return request('POST', '/api/merchant/products', data, true);
  },

  async update(id, data) {
    return request('PUT', `/api/merchant/products/${id}`, data, true);
  },

  async delete(id) {
    return request('DELETE', `/api/merchant/products/${id}`, null, true);
  },
};

/* ============================================================
   订单（待接入）
   ============================================================ */
const OrderAPI = {
  async getList() {
    return request(
      'GET',
      '/api/orders',
      null,
      true
    );
  },
  async create(goodsId, quantity = 1) {
    return request(
      'POST',
      '/api/orders/buy',
      {
        goods_id: goodsId,
        quantity: quantity,
      },
      true
    );
  },

  async getMerchantOrders() {
    // return request('GET', '/api/merchant/orders', null, true);
    return null;
  },
};

/* ============================================================
   购物车（已完成）
   ============================================================ */
const CartAPI = {
  async getCart() {
    return request('GET', '/api/cart', null, true);
  },
  async addItem(goodsId, quantity = 1) {
    return request('POST', '/api/cart', { goods_id: goodsId, quantity }, true);
  },
  async removeItem(goodsId) {
    return request('DELETE', `/api/cart/${goodsId}`, null, true);
  },
  async updateQuantity(goodsId, quantity) {
    return request('PUT', `/api/cart/${goodsId}`, { quantity }, true);
  },
  async checkout() {
    return request('POST', '/api/cart/checkout', null, true);
  }
};

/* ============================================================
   聊天（待接入）
   ============================================================ */
const ChatAPI = {
  async getList() {
    // return request('GET', '/api/chats', null, true);
    return null;
  },
  async getMessages(chatId) {
    // return request('GET', `/api/chats/${chatId}/messages`, null, true);
    return null;
  },
  async sendMessage(chatId, content) {
    // return request('POST', `/api/chats/${chatId}/messages`, { content }, true);
    return null;
  },
};

/* ============================================================
   举报（待接入）
   ============================================================ */
const ReportAPI = {
  async getList() {
    // return request('GET', '/api/admin/reports', null, true);
    return null;
  },
  async handle(reportId, action) {
    // return request('POST', `/api/admin/reports/${reportId}/handle`, { action }, true);
    return null;
  },
};

/* ============================================================
   商家统计（待接入）
   ============================================================ */
const MerchantAPI = {
  async getStats() {
    // return request('GET', '/api/merchant/stats', null, true);
    return null;
  },
};
