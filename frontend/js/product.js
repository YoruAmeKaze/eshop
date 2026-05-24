/* ============================================================
   product.js — 商品详情页逻辑
   ============================================================ */

let currentProduct = null;

const CATEGORY_MAP = {
    electronic: '数码', clothes: '服饰', living: '家居',
    beauty: '美妆', sports: '运动', baby: '母婴',
    food: '食品', book: '图书', others: '其他'
};

/* ---- 入口 ---- */
window.openProductDetail = async function (id) {
    window._prevPage = document.querySelector('.page.active')?.id;
    window.showPage('page-product');

    const container = document.getElementById('product-detail-content');
    container.innerHTML = '<div class="loading-state">加载中...</div>';

    // 清理旧的操作栏
    const oldBar = document.getElementById('product-action-bar');
    if (oldBar) oldBar.remove();

    try {
        const data = await ProductAPI.getDetail(id);
        if (data && data.status === 'success') {
            currentProduct = data.data;
            renderProductDetail(container, data.data);
        } else {
            container.innerHTML = `
        <div class="error-state">
          <p>商品不存在或已下架</p>
          <button class="retry-btn" onclick="leaveProductDetail()">返回</button>
        </div>`;
        }
    } catch (e) {
        container.innerHTML = `
      <div class="error-state">
        <p>加载失败，请检查网络</p>
        <button class="retry-btn" onclick="openProductDetail(${id})">重试</button>
      </div>`;
    }
};

/* ---- 渲染详情 ---- */
function renderProductDetail(container, p) {
    container.innerHTML = `
    <div class="product-image-box">
      ${p.image_url ? `<img src="${p.image_url}">` : '🛍️'}
    </div>

    <div class="card">
      <div class="product-price-large">¥${p.price}</div>
      <div class="product-title">${p.name}</div>
      <span class="tag tag-consumer">${CATEGORY_MAP[p.category] || p.category}</span>
    </div>

    <div class="card">
      <div class="product-desc-title">商品详情</div>
      <div class="product-desc-body">${p.description || '暂无描述'}</div>
    </div>

    <div class="card" onclick="openShop(${p.merchant_id})">
      <div class="shop-entry">
        <div class="shop-entry-icon">🏪</div>
        <div class="shop-entry-info">
          <div class="shop-name">进入店铺</div>
          <div class="shop-sub">查看该商家的更多商品</div>
        </div>
        <span class="shop-entry-arrow">›</span>
      </div>
    </div>

    <div class="product-action-spacer"></div>
  `;

    renderActionBar(p);
}

/* ---- 底部操作栏 ---- */
function renderActionBar(p) {
    const bar = document.createElement('div');
    bar.id = 'product-action-bar';
    bar.className = 'product-action-bar';
    bar.innerHTML = `
    <button class="btn-cart" onclick="addToCart(${p.id})">🛒 加入购物车</button>
    <button class="btn-buy"  onclick="buyNow(${p.id})">立即购买</button>
  `;
    document.getElementById('page-product').appendChild(bar);
}

/* ---- 加入购物车 ---- */
window.addToCart = async function (productId) {
    if (!window.currentUser) { window.showPage('page-login'); return; }
    try {
        const data = await CartAPI.addItem(productId, 1);
        if (data && data.status === 'success') {
            window.showToast('已加入购物车 🛒');
        } else {
            window.showToast(data?.message || '加入失败');
        }
    } catch (e) {
        window.showToast('操作失败，请重试');
    }
};

/* ---- 立即购买 ---- */
window.buyNow = async function (productId) {
    if (!window.currentUser) {
        window.showPage('page-login');
        return;
    }

    try {
        const data = await OrderAPI.create(productId, 1);

        if (data && data.status === 'success') {

            window.showToast('下单成功！');

            // 返回消费者页面
            window.showPage('page-consumer');

            // 切换到订单 tab
            document.querySelectorAll('.c-tab')
                .forEach(t => t.style.display = 'none');

            const ordersTab = document.getElementById('c-orders');

            if (ordersTab) {
                ordersTab.style.display = 'flex';
                ordersTab.style.flexDirection = 'column';
            }

            // 底部导航高亮
            document.querySelectorAll('#page-consumer .tab')
                .forEach(t => t.classList.remove('active'));

            const orderBtn = document.querySelector(
                '#page-consumer .tab[data-tab="orders"]'
            );

            if (orderBtn) {
                orderBtn.classList.add('active');
            }

            // 加载订单
            loadOrders();

        } else {
            window.showToast(data?.message || '下单失败');
        }

    } catch (e) {
        console.error(e);
        window.showToast('操作失败，请重试');
    }
};

/* ---- 进入店铺 ---- */
window.openShop = function (merchantId) {
    window.showToast('店铺页面开发中');
};

/* ---- 返回 ---- */
window.leaveProductDetail = function () {
    const bar = document.getElementById('product-action-bar');
    if (bar) bar.remove();
    const prev = window._prevPage || 'page-consumer';
    window.showPage(prev);
};
