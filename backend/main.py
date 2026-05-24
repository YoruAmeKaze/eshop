from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

import auth
from database import user_database, shop, cart

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 测试阶段直接全开
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RegisterRequest(BaseModel):
    name: str
    password: str
    roles: str
    tel: Optional[str] = None

class LoginRequest(BaseModel):
    name: str
    password: str

class ProductRequest(BaseModel):
    name: str
    description: str
    price: float
    category: str
    image_url: Optional[str] = None

class CartAddRequest(BaseModel):
    goods_id: int
    quantity: int = 1

class CartUpdateRequest(BaseModel):
    quantity: int

class BuyRequest(BaseModel):
    goods_id: int
    quantity: int

VALID_CATEGORIES = {'electronic','clothes','living','beauty','sports','baby','food','book','others'}

@app.post("/api/register")
async def register(data: RegisterRequest):
    db = user_database()
    result = db.create_user(data.dict())
    db.close()
    return result

@app.post("/api/login")
async def login(data: LoginRequest):
    db = user_database()
    result = db.login(data.dict())
    db.close()
    if result['status'] == 'success':
        token = auth.create_access_token({
            'id': result['id'],
            'roles': result['roles']
            })
        return {'status': 'success',
                'token': token,
                'roles': result['roles'],
                'id': result['id']
                }
    return result

@app.get("/api/user/me")
async def get_users(request: Request):
    db = user_database()
    
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="缺少token")
    token = auth_header.split(" ", 1)[1] if " " in auth_header else auth_header

    token_data = auth.decode_token(token)
    result = db.find_users(token_data["id"])
    db.close()
    return result

@app.get("/api/merchant/products")
async def get_shop(request: Request):
    db = shop()
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="缺少token")
    token = auth_header.split(" ", 1)[1] if " " in auth_header else auth_header

    token_data = auth.decode_token(token)
    result = db.list_goods_merchant(token_data["id"])
    db.close()
    return result

@app.post("/api/merchant/products")
async def add_product(data: ProductRequest, request: Request):
    db = shop()
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="缺少token")
    token = auth_header.split(" ", 1)[1] if " " in auth_header else auth_header
    if category and category not in VALID_CATEGORIES:
        raise HTTPException(status_code=400, detail="无效的分类")

    token_data = auth.decode_token(token)
    result = db.add_goods(token_data["id"], data.name, data.description, data.price, data.category, data.image_url)
    db.close()
    return result

@app.put("/api/merchant/products/{product_id}")
async def edit_product(product_id: int, data: ProductRequest, request: Request):
    db = shop()
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="缺少token")
    token = auth_header.split(" ", 1)[1] if " " in auth_header else auth_header
    if category and category not in VALID_CATEGORIES:
        raise HTTPException(status_code=400, detail="无效的分类")

    token_data = auth.decode_token(token)
    result = db.update_goods(token_data["id"], product_id, data.name, data.description, data.price, data.category, data.image_url)
    db.close()
    return result

@app.delete("/api/merchant/products/{product_id}")
async def delete_product(product_id: int, request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header: 
        raise HTTPException(status_code=401, detail="缺少token")
    token = auth_header.split(" ", 1)[1] if " " in auth_header else auth_header
    if category and category not in VALID_CATEGORIES:
        raise HTTPException(status_code=400, detail="无效的分类")

    token_data = auth.decode_token(token)
    db = shop()
    result = db.delete_goods(token_data["id"], product_id)
    db.close()
    return result

@app.get("/api/products/random")
async def get_random_products(request: Request, category: Optional[str] = None):
    auth_headers = request.headers.get("Authorization")
    if not auth_headers:
        raise HTTPException(status_code=401, detail="缺少token")
    token = auth_headers.split(" ", 1)[1] if " " in auth_headers else auth_headers

    db = shop()
    result = db.random_goods(category)
    db.close()
    return result

@app.get("/api/products")
async def get_products(request: Request, page: int = 1, limit: int = 10, category: str = None):
    db = shop()
    result = db.list_goods_consumer(page, limit, category)
    db.close()
    return result

@app.get("/api/products/{product_id}")
async def get_product_detail(request: Request, product_id: int):
    db = shop()
    result = db.get_product_detail(product_id)
    db.close()
    if result['status'] == 'error':
        raise HTTPException(status_code=404, detail="商品不存在")
    return result

@app.get("/api/cart")
async def get_cart(request: Request): 
    db = cart()
    
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="缺少token")
    token = auth_header.split(" ", 1)[1] if " " in auth_header else auth_header
    
    token_data = auth.decode_token(token)
    result = db.get_cart(token_data["id"])
    db.close()
    return result

@app.post("/api/cart")
async def add_to_cart(data: CartAddRequest, request: Request):
    db = cart()
    
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="缺少token")
    token = auth_header.split(" ", 1)[1] if " " in auth_header else auth_header
    
    token_data = auth.decode_token(token)
    result = db.add_to_cart(token_data["id"], data.goods_id, data.quantity)
    db.close()
    return result

@app.delete("/api/cart/{product_id}")
async def delete_from_cart(product_id: int, request: Request):
    db = cart()
    
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="缺少token")
    token = auth_header.split(" ", 1)[1] if " " in auth_header else auth_header
    
    token_data = auth.decode_token(token)
    result = db.delete_from_cart(token_data["id"], product_id)
    db.close()
    return result

@app.put("/api/cart/{product_id}")
async def adjust_cart(product_id: int, data: CartUpdateRequest, request: Request):
    db = cart()
    
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="缺少token")
    token = auth_header.split(" ", 1)[1] if " " in auth_header else auth_header
    
    token_data = auth.decode_token(token)
    result = db.adjust_number(token_data["id"], product_id, data.quantity)
    db.close()
    return result

@app.post("/api/orders/buy")
async def buy_goods(data: BuyRequest, request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="缺少token")
    token = auth_header.split(" ", 1)[1] if " " in auth_header else auth_header
    
    token_data = auth.decode_token(token)
    db = goods()
    result = db.buy_goods(token_data["id"], data.goods_id, data.quantity)
    db.close()
    return result

@app.get("/api/orders")
async def get_orders(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="缺少token")
    token = auth_header.split(" ", 1)[1] if " " in auth_header else auth_header
    
    token_data = auth.decode_token(token)
    db = goods()
    result = db.get_orders_consumer(token_data["id"])
    db.close()
    return result