可以，我给你整理一个适合你现在阶段（Compose + Nginx + K8s 已完成）的 **标准 README.md**

---

# Kazever Shop

一个用于学习 **全栈开发 + 容器化 + Kubernetes 运维** 的迷你电商系统。

---

## 📌 项目简介

Kazever Shop 是一个前后端分离的模拟电商平台，用于实践：

* Web 全栈开发
* Docker / Compose 容器化
* Kubernetes 集群部署
* CI/CD 基础流程
* 微服务拆分思维

---

## 🧱 技术架构

### 前端

* 原生 HTML / CSS / JavaScript
* SPA 单页应用（单入口 `index.html`）
* 自定义路由系统
* API 层统一封装（`api.js`）
* JWT 存储于 `localStorage`

主要模块：

* consumer（用户端）
* merchant（商家端）
* admin（管理端）

---

### 后端

* FastAPI（Python）
* MySQL（关系型数据库）
* PyMySQL 连接数据库
* JWT 鉴权（python-jose）
* SHA256 密码加密

数据库名：

```
eshop
```

---

### 数据库表结构

```sql
users  (id, name, password, tel, roles)
goods  (id, merchant_id, name, description, price, category, image_url, created_at)
cart   (id, user_id, goods_id, quantity, created_at)
UNIQUE KEY (user_id, goods_id)
```

---

### 用户角色

* consumer：消费者
* merchant：商家
* admin：管理员

JWT 中携带 `id + roles`，前端根据 roles 控制页面权限与跳转。

---

## 🚀 已实现功能

### 后端 API

* 用户系统

  * 注册 `/api/register`
  * 登录 `/api/login`
  * 当前用户 `/api/user/me`

* 商品系统

  * 商品列表 `/api/products`
  * 商品详情 `/api/products/{id}`
  * 商家商品 CRUD

* 购物车系统

  * 添加商品
  * 修改数量
  * 删除商品
  * 查询购物车（JOIN goods）

---

### 前端功能

* 登录 / 注册
* 商品列表展示（分页 + 分类）
* 商品详情页
* 购物车
* 商家后台 CRUD
* 管理员页面（占位）
* 统一 Toast 提示系统

---

## 🐳 部署方式

### 1. Docker Compose（旧版本）

* nginx + backend + mysql
* 本地 registry 镜像管理
* Nginx 提供前端静态资源 + API 反向代理

---

### 2. Kubernetes（当前主力）

已完成：

* kubeadm 单节点集群
* containerd 运行时
* Namespace 隔离（eshop）
* Deployment / Service
* ConfigMap / Secret
* MySQL PVC 持久化
* CoreDNS 服务发现

服务访问方式：

```
backend: eshop-backend
mysql: eshop-mysql
```

---

## ☸️ Kubernetes 架构

```
Ingress（未完成）
    ↓
Frontend Service（未来）
    ↓
Backend Service
    ↓
MySQL Service
    ↓
PersistentVolume
```

---

## 📦 目录结构

```
eshop/
├── frontend/
├── backend/
├── k8s/
│   ├── namespace.yaml
│   ├── mysql.yaml
│   ├── backend.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── pv-pvc.yaml
│   └── ingress.yaml（未完成）
├── compose.yaml
└── README.md
```

---

## 🔧 开发约定

* 所有 API 统一 `/api` 前缀
* 前端统一通过 `api.js` 请求
* 禁止 HTML 内联 onclick
* JWT 存储 key：`kv_token`
* 所有服务通过 Service DNS 通信（K8s）
* MySQL host：

  * Compose：`eshop-mysql`
  * K8s：`eshop-mysql.eshop.svc.cluster.local`

---

## 📈 当前进度

### 已完成

* 用户系统
* 商品系统（完整 CRUD）
* 购物车系统
* 前端 SPA 架构
* Docker Compose 部署
* Kubernetes 基础集群
* K8s 部署 backend + mysql
* PVC 持久化
* Service / ConfigMap / Secret

---

### 进行中

* 前端 K8s 化部署
* Ingress 暴露服务

---

### 未完成

* 订单系统
* 消息系统
* 管理员举报系统
* 搜索功能
* CI/CD 自动部署（CD）
* 日志系统（ELK / Loki）
* 监控系统（Prometheus）

---

## 🎯 下一步目标

1. 完整 K8s 化前端（Nginx Deployment）
2. Ingress 暴露统一入口
3. 接入 Helm（可选）
4. CI/CD 自动部署到 K8s
5. 微服务拆分（订单 / 消息）

---