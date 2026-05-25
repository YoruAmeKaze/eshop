import pymysql
import hashlib
from fastapi import HTTPException

def hash(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

class user_database:
    def __init__(self):
        self.conn = pymysql.connect(
            host='eshop-mysql',
            user='root', 
            password='123456', 
            db='eshop'
        )
        self.cursor = self.conn.cursor()

    def close(self):
        self.cursor.close()
        self.conn.close()

    def check_exist(self, name, kind):
        if kind not in ['name', 'tel', 'id']:
            return False
        sql = f"SELECT * FROM users WHERE {kind} = %s LIMIT 1"
        self.cursor.execute(sql, (name,))
        return self.cursor.fetchone() is None

    def check_empty(self, message):
        if not message or message.strip() == '':
            return True
        return False

    def create_user(self, info):
        name = info['name']
        password = info['password']
        roles = info['roles']
        tel = info.get('tel')
        if self.check_empty(name):
            return {'status': 'error',
                'message': '用户名不能为空'
            }
        if self.check_empty(password):
            return {'status': 'error',
                'message': '密码不能为空'
            }
        if not self.check_exist(name, 'name'):
            return {'status': 'error',
                'message': '用户名已存在'
            }
        if roles not in ['consumer', 'merchant']:
            return {'status': 'error',
                'message': '角色必须是consumer或merchant'
            }
        password = hash(password)
        sql = 'insert into users (name, password, roles, tel) values (%s, %s, %s, %s)'
        self.cursor.execute(sql, (name, password, roles, tel))
        self.conn.commit()
        return {'status': 'success',
                'message': '用户创建成功'
            }
    
    def login(self, info):
        name = info['name']
        password = info['password']
        if self.check_empty(name):
            return {'status': 'error',
                'message': '用户名不能为空'
            }
        if self.check_empty(password):
            return {'status': 'error',
                'message': '密码不能为空'
            }
        sql = 'select * from users where name = %s'
        self.cursor.execute(sql, (name,))
        result = self.cursor.fetchone()
        if not result:
            return {'status': 'error',
                    'message': '用户不存在'
                }
        if result[2] == hash(password):
            return {'status': 'success',
                    'message': '登录成功',
                    'roles': result[4],
                    'id': result[0]
                }
        else:
            return {'status': 'error',
                    'message': '密码错误'
                }
        
    def find_users(self, id):
        sql = 'select * from users where id = %s'
        self.cursor.execute(sql, (id,))
        result = self.cursor.fetchone()
        if result:
            return {
                "status": "success",
                "message": "用户查询成功",
                "data": {
                    "id": result[0],
                    "name": result[1],
                    "tel": result[3],
                    "roles": result[4]
                }
        }
        else:
            raise HTTPException(status_code=404, detail="用户不存在")
        
class shop():
    def __init__(self):
        self.conn = pymysql.connect(
            host='eshop-mysql',
            user='root', 
            password='123456', 
            db='eshop'
        )
        self.cursor = self.conn.cursor()

    def close(self):
        self.cursor.close()
        self.conn.close()

    def check_merchant_exist(self, id):
        sql = 'select * from users where id = %s and roles = "merchant"'
        self.cursor.execute(sql, (id,))
        if not self.cursor.fetchone():
            raise HTTPException(status_code=404, detail="商户不存在")
        
    def check_goods_exist(self, id, merchant_id):
        sql = 'select * from goods where id = %s and merchant_id = %s'
        self.cursor.execute(sql, (id, merchant_id))
        if not self.cursor.fetchone():
            raise HTTPException(status_code=404, detail="商品不存在")

    def list_goods_merchant(self,id):
        self.check_merchant_exist(id)
        data = []
        sql = 'select * from goods where merchant_id = %s'
        self.cursor.execute(sql, (id,))
        result = self.cursor.fetchall()
        for row in result:
            data.append({
                'id': row[0],
                'merchant_id': row[1],
                'name': row[2],
                'description': row[3],
                'price': float(row[4]),
                'category': row[5],
                'image_url': row[6]
            })
        return {
            'status': 'success',
            'message': '查询成功',
            'data': data
        }
    
    def add_goods(self, merchant_id, name, description, price, category, image_url):
        self.check_merchant_exist(merchant_id)
        sql = 'insert into goods (merchant_id, name, description, price, category, image_url) values (%s, %s, %s, %s, %s, %s)'
        self.cursor.execute(sql, (merchant_id, name, description, price, category, image_url))
        self.conn.commit()
        return {
            'status': 'success',
            'message': '添加成功',
            'data': {
                'id': self.cursor.lastrowid,
                'merchant_id': merchant_id,
                'name': name,
                'description': description,
                'price': price,
                'category': category,
                'image_url': image_url
            }
        }
    
    def update_goods(self, merchant_id, id, name, description, price, category, image_url):
        self.check_merchant_exist(merchant_id)
        self.check_goods_exist(id, merchant_id)

        sql = 'update goods set name = %s, description = %s, price = %s, category = %s, image_url = %s where id = %s and merchant_id = %s'
        self.cursor.execute(sql, (name, description, price, category, image_url, id, merchant_id))
        self.conn.commit()
        return {
            'status': 'success',
            'message': '修改成功',
            'data': {
                'id': id,
                'merchant_id': merchant_id,
                'name': name,
                'description': description,
                'price': price,
                'category': category,
                'image_url': image_url
            }
        }

    def delete_goods(self, merchant_id, id):
        self.check_merchant_exist(merchant_id)
        self.check_goods_exist(id, merchant_id)

        sql = 'delete from goods where id = %s and merchant_id = %s'
        self.cursor.execute(sql, (id, merchant_id))
        self.conn.commit()
        return {
            'status': 'success',
            'message': '删除成功'
        }

    def random_goods(self, category = None):
        if category:
            sql = 'select * from goods where category = %s order by rand() limit 10'
            self.cursor.execute(sql, (category,))
        else:
            sql = 'select * from goods order by rand() limit 10'
            self.cursor.execute(sql)
        result = self.cursor.fetchall()
        data = []
        for row in result:
            data.append({
                'id': row[0],
                'merchant_id': row[1],
                'name': row[2],
                'description': row[3],
                'price': float(row[4]),
                'category': row[5],
                'image_url': row[6]
            })
        return {
            'status': 'success',
            'message': '查询成功',
            'data': data
        }

    def list_goods_consumer(self, page=1, limit=10, category=None):
        page = page or 1
        limit = limit or 10
        if category in [None, "", "null", "undefined"]:
            category = None
        print(page, limit, category)
        offset = (page - 1) * limit
        if category:
            sql = 'select * from goods where category = %s limit %s offset %s'
            self.cursor.execute(sql, (category, limit, offset))
        else:
            sql = 'select * from goods limit %s offset %s'
            self.cursor.execute(sql, (limit, offset))
        result = self.cursor.fetchall()
        data = []
        for row in result:
            data.append({
                'id': row[0],
                'merchant_id': row[1],
                'name': row[2],
                'description': row[3],
                'price': float(row[4]),
                'category': row[5],
                'image_url': row[6]
            })
        return {
            'status': 'success',
            'message': '查询成功',
            'data': data
        }

    def get_product_detail(self, id):
        sql = 'select * from goods where id = %s'
        self.cursor.execute(sql, (id,))
        result = self.cursor.fetchone()
        if result:
            return {
                'status': 'success',
                'message': '查询成功',
                'data': {
                    'id': result[0],
                    'merchant_id': result[1],
                    'name': result[2],
                    'description': result[3],
                    'price': float(result[4]),
                    'category': result[5],
                    'image_url': result[6]
                }
            }
        return {
            'status': 'error',
            'message': '商品不存在'
        }



class cart():
    def __init__(self):
        self.conn = pymysql.connect(
            host='eshop-mysql',
            user='root',
            password='123456',
            db='eshop'
        )
        self.cursor = self.conn.cursor()

    def close(self):
        self.cursor.close()
        self.conn.close()

    def add_to_cart(self, user_id, goods_id, quantity):
        sql = ('INSERT INTO cart (user_id, goods_id, quantity) VALUES (%s, %s, %s) '
                'ON DUPLICATE KEY UPDATE quantity = quantity + %s')
        self.cursor.execute(sql, (user_id, goods_id, quantity, quantity))
        self.conn.commit()
        return {
            'status': 'success',
            'message': '添加到购物车成功'
        }

    def delete_from_cart(self, user_id, goods_id):
        sql = 'DELETE FROM cart WHERE user_id = %s AND goods_id = %s'
        self.cursor.execute(sql, (user_id, goods_id))
        self.conn.commit()
        return {
            'status': 'success',
            'message': '从购物车删除成功'
        }

    def adjust_number(self, user_id, goods_id, quantity):
        sql = 'UPDATE cart SET quantity = %s WHERE user_id = %s AND goods_id = %s'
        self.cursor.execute(sql, (quantity, user_id, goods_id))
        self.conn.commit()
        return {
            'status': 'success',
            'message': '调整购物车数量成功'
        }

    def get_cart(self, user_id):
        sql = '''
            SELECT c.id, c.goods_id, c.quantity, g.name, g.price, g.image_url
            FROM cart c
            JOIN goods g ON c.goods_id = g.id
            WHERE c.user_id = %s
        '''
        self.cursor.execute(sql, (user_id,))
        result = self.cursor.fetchall()
        return {
        'status': 'success',
        'data': [{
            'cart_id':   row[0],
            'goods_id':  row[1],
            'quantity':  row[2],
            'name':      row[3],
            'price':     float(row[4]),
            'image_url': row[5]
        } for row in result]  
    }
class order():
    def __init__(self):
        self.conn = pymysql.connect(
            host='eshop-mysql',
            user='root',
            password='123456',
            db='eshop'
        )

    def close(self):
        self.conn.close()

    def create_order(self, user_id, goods_id, merchant_id, quantity, price, total_price):
        sql = 'INSERT INTO orders (user_id, goods_id, merchant_id, quantity, price, total_price) VALUES (%s, %s, %s, %s, %s, %s)'
        cursor = self.conn.cursor()
        cursor.execute(sql, (user_id, goods_id, merchant_id, quantity, price, total_price))
        return {
            'status': 'success',
            'message': '订单创建成功'
        }

    def get_orders_consumer(self, user_id):
        sql = '''
            SELECT o.id, o.goods_id, o.merchant_id, o.quantity, o.price, o.total_price, g.name
            FROM orders o
            JOIN goods g ON o.goods_id = g.id
            WHERE o.user_id = %s
        '''
        cursor = self.conn.cursor()
        cursor.execute(sql, (user_id,))
        result = cursor.fetchall()
        return {
            'status': 'success',
            'data': [{
                'order_id':   row[0],
                'goods_id':   row[1],
                'merchant_id':row[2],
                'quantity':   row[3],
                'price':      float(row[4]),
                'total_price':float(row[5]),
                'name':       row[6],
            } for row in result]  
        }

    def buy_goods(self, user_id, goods_id, quantity):
        sql = 'select * from goods where id = %s'
        cursor = self.conn.cursor()
        cursor.execute(sql, (goods_id,))
        result = cursor.fetchone()
        if not result:
            return {
                'status': 'error',
                'message': '商品不存在'
            }
        price = float(result[4])
        merchant_id = result[1]
        total_price = price * quantity  
        result = self.create_order(
            user_id,
            goods_id, 
            merchant_id, 
            quantity, 
            price, 
            total_price
        )
        self.conn.commit()
        return result

    def buy_cart(self, user_id):
        sql = '''
            SELECT c.goods_id, c.quantity, g.price, g.merchant_id
            FROM cart c
            JOIN goods g ON c.goods_id = g.id
            WHERE c.user_id = %s
        '''
        cursor = self.conn.cursor()
        cursor.execute(sql, (user_id,))
        result = cursor.fetchall()
        if not result:
            return {
                'status': 'error',
                'message': '购物车为空'
            }
        for row in result:
            goods_id = row[0]
            quantity = row[1]
            price = float(row[2])
            merchant_id = row[3]
            total_price = price * quantity
            self.create_order(
                user_id,
                goods_id,
                merchant_id,
                quantity,
                price,
                total_price
            )
        # 清空购物车
        sql = 'DELETE FROM cart WHERE user_id = %s'
        cursor.execute(sql, (user_id,))
        self.conn.commit()
        return {
            'status': 'success',
            'message': '购买成功'
        }

    