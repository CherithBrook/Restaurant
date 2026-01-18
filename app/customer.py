from supabase import create_client, Client
import os
import json

# Supabase配置（替换为你的实际配置）
SUPABASE_URL = "https://lkadifukazgphwzkfuez.supabase.co"
SUPABASE_KEY = "sb_secret_71F1tqMywPNfvbxK9lUj_g_-QMiHOHJ"

# 创建Supabase客户端
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class Customer:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.username = self._get_username()
        self.current_table_id = None
        self.current_table_number = None
    
    def _get_username(self) -> str:
        """获取用户名"""
        try:
            response = supabase.table("users").select("real_name").eq("user_id", self.user_id).single().execute()
            return response.data["real_name"] if response.data else "未知顾客"
        except Exception as e:
            print(f"获取用户名失败：{str(e)}")
            return "未知顾客"
    
    def view_available_tables(self) -> list:
        """查看所有空闲桌台"""
        try:
            response = supabase.table("tables")\
                .select("table_id, table_number, table_type, capacity")\
                .eq("status", "空闲")\
                .order("table_type")\
                .order("table_number")\
                .execute()
            
            if not response.data:
                print("暂无空闲桌台")
                return []
            
            print("\n" + "="*50)
            print("聚香园 - 空闲桌台列表")
            print("="*50)
            print(f"{'桌台ID':<6} {'桌台号':<8} {'类型':<8} {'容量':<4}")
            print("-"*50)
            for table in response.data:
                print(f"{table['table_id']:<6} {table['table_number']:<8} {table['table_type']:<8} {table['capacity']:<4}")
            print("="*50 + "\n")
            return response.data
        except Exception as e:
            print(f"查看空闲桌台失败：{str(e)}")
            return []
    
    def bind_table(self, table_id: int) -> bool:
        """绑定桌台（开台）"""
        try:
            # 检查桌台是否空闲
            table_response = supabase.table("tables").select("table_id, table_number, status").eq("table_id", table_id).single().execute()
            if not table_response.data:
                print(f"桌台ID {table_id} 不存在")
                return False
            
            if table_response.data["status"] != "空闲":
                print(f"桌台 {table_response.data['table_number']} 当前状态为 {table_response.data['status']}，无法绑定")
                return False
            
            # 调用开台存储过程
            result = call_procedure("open_table", [table_id, self.user_id])
            if result:
                self.current_table_id = table_id
                self.current_table_number = table_response.data["table_number"]
                print(f"绑定成功！当前桌台：{self.current_table_number}")
                return True
            else:
                print("桌台绑定失败")
                return False
        except Exception as e:
            print(f"绑定桌台失败：{str(e)}")
            return False
    
    def unbind_table(self) -> bool:
        """解除桌台绑定（仅未结账时可用）"""
        if not self.current_table_id:
            print("当前未绑定任何桌台")
            return False
        
        try:
            # 检查订单状态
            order_response = supabase.table("orders").select("status").eq("table_id", self.current_table_id).eq("status", "未结账").single().execute()
            if order_response.data:
                print("当前桌台存在未结账订单，无法解除绑定")
                return False
            
            # 更新桌台状态为空闲（如果是待清理状态）
            supabase.table("tables").update({"status": "空闲", "updated_at": "now()"}).eq("table_id", self.current_table_id).execute()
            
            print(f"已解除桌台 {self.current_table_number} 的绑定")
            self.current_table_id = None
            self.current_table_number = None
            return True
        except Exception as e:
            print(f"解除绑定失败：{str(e)}")
            return False
    
    def view_all_dishes(self) -> list:
        """查看所有上架菜品及口味选项"""
        try:
            # 首先获取所有上架菜品
            dishes_response = supabase.table("dishes")\
                .select("dish_id, dish_name, category_id, price, description")\
                .eq("is_active", True)\
                .order("sort_order")\
                .execute()
            
            if not dishes_response.data:
                print("暂无上架菜品")
                return []
            
            result = []
            for dish in dishes_response.data:
                # 获取分类名称
                category_response = supabase.table("dish_categories")\
                    .select("category_name")\
                    .eq("category_id", dish["category_id"])\
                    .single()\
                    .execute()
                
                if category_response.data:
                    dish["category_name"] = category_response.data["category_name"]
                else:
                    dish["category_name"] = "未知分类"
                
                # 获取口味选项
                taste_response = supabase.rpc("get_dish_tastes", {"p_dish_id": dish["dish_id"]}).execute()
                dish["taste_options"] = taste_response.data if taste_response.data else []
                
                result.append(dish)
            
            print("\n" + "="*80)
            print("聚香园 - 菜品列表")
            print("="*80)
            print(f"{'菜品ID':<6} {'菜品名称':<10} {'分类':<6} {'价格':<6} {'描述':<30} {'口味选项':<30}")
            print("-"*80)
            
            for dish in result:
                taste_info = []
                for taste in dish["taste_options"]:
                    required_str = "(必选)" if taste.get("is_required") else "(可选)"
                    taste_info.append(f"{taste['taste_name']}{required_str}")
                
                taste_str = " | ".join(taste_info)[:28] + "..." if len(" | ".join(taste_info)) > 30 else " | ".join(taste_info)
                desc = dish.get("description", "")
                desc = desc[:28] + "..." if desc and len(desc) > 30 else desc or ""
                print(f"{dish['dish_id']:<6} {dish['dish_name']:<10} {dish['category_name']:<6} {dish['price']:<6.2f} {desc:<30} {taste_str:<30}")
            
            print("="*80 + "\n")
            return result
        except Exception as e:
            print(f"查看菜品失败：{str(e)}")
            return []
    
    def get_dish_required_tastes(self, dish_id: int) -> list:
        """获取指定菜品的必选口味"""
        try:
            response = supabase.rpc("get_required_tastes", {"p_dish_id": dish_id}).execute()
            return response.data
        except Exception as e:
            print(f"获取必选口味失败：{str(e)}")
            return []
    
    def select_taste_options(self, dish_id: int) -> dict:
        """选择菜品口味"""
        required_tastes = self.get_dish_required_tastes(dish_id)
        all_tastes = self._get_all_dish_tastes(dish_id)
        
        taste_choices = {}
        
        print(f"\n请为菜品选择口味：")
        
        # 处理必选口味
        if required_tastes:
            print("必选口味：")
            for taste in required_tastes:
                while True:
                    choice = input(f"  {taste['taste_name']}（输入口味ID {taste['taste_id']}）：")
                    try:
                        choice_id = int(choice)
                        if choice_id == taste['taste_id']:
                            taste_choices[str(choice_id)] = taste['taste_name']
                            break
                        else:
                            print(f"输入错误！请输入正确的口味ID {taste['taste_id']}")
                    except ValueError:
                        print("输入错误！请输入数字类型的口味ID")
        
        # 处理可选口味
        optional_tastes = [t for t in all_tastes if t['taste_id'] not in [rt['taste_id'] for rt in required_tastes]]
        if optional_tastes:
            print("\n可选口味（输入口味ID选择，多个用逗号分隔，直接回车跳过）：")
            for taste in optional_tastes:
                print(f"  {taste['taste_id']}: {taste['taste_name']}")
            
            choice_input = input("请选择可选口味：")
            if choice_input.strip():
                choice_ids = [c.strip() for c in choice_input.split(",")]
                for cid in choice_ids:
                    try:
                        taste_id = int(cid)
                        taste = next((t for t in optional_tastes if t['taste_id'] == taste_id), None)
                        if taste:
                            taste_choices[str(taste_id)] = taste['taste_name']
                    except ValueError:
                        print(f"无效的口味ID：{cid}，已忽略")
        
        return taste_choices
    
    def _get_all_dish_tastes(self, dish_id: int) -> list:
        """获取指定菜品的所有口味选项"""
        try:
            response = supabase.rpc("get_dish_tastes", {"p_dish_id": dish_id}).execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"获取菜品口味失败：{str(e)}")
            return []
    
    def place_order(self, dish_id: int, quantity: int, taste_choices: dict) -> bool:
        """提交订单（点餐/加菜）"""
        if not self.current_table_id:
            print("请先绑定桌台再点餐")
            return False
        
        try:
            # 构建菜品列表参数
            dish_list = [
                {
                    "dish_id": dish_id,
                    "quantity": quantity,
                    "taste_choices": taste_choices
                }
            ]
            dish_list_json = json.dumps(dish_list)
            
            # 调用点餐存储过程
            result = call_procedure("place_order", [self.current_table_id, self.user_id, dish_list_json])
            if result:
                order_id = result[0]["p_order_id"]
                print(f"点餐成功！订单ID：{order_id}")
                return True
            else:
                print("点餐失败")
                return False
        except Exception as e:
            print(f"点餐失败：{str(e)}")
            return False
    
    def urge_dish(self, order_item_id: int) -> bool:
        """催菜"""
        if not self.current_table_id:
            print("请先绑定桌台")
            return False
        
        try:
            # 检查该菜品是否属于当前桌台
            # 首先获取订单ID
            order_response = supabase.table("orders")\
                .select("order_id")\
                .eq("table_id", self.current_table_id)\
                .eq("status", "未结账")\
                .single()\
                .execute()
            
            if not order_response.data:
                print("当前桌台无未结账订单")
                return False
            
            order_id = order_response.data["order_id"]
            
            # 检查菜品是否属于该订单
            item_response = supabase.table("order_items")\
                .select("order_item_id")\
                .eq("order_id", order_id)\
                .eq("order_item_id", order_item_id)\
                .single()\
                .execute()
            
            if not item_response.data:
                print(f"菜品ID {order_item_id} 不存在或不属于当前桌台")
                return False
            
            # 调用催菜存储过程
            call_procedure("urge_dish", [order_item_id])
            print(f"催菜成功！菜品ID：{order_item_id}")
            return True
        except Exception as e:
            print(f"催菜失败：{str(e)}")
            return False
    
    def view_bill(self) -> list:
        """查看当前桌台账单"""
        if not self.current_table_id:
            print("请先绑定桌台")
            return []
        
        try:
            # 获取当前桌台的未结账订单
            order_response = supabase.table("orders")\
                .select("order_id, discount, total_amount")\
                .eq("table_id", self.current_table_id)\
                .eq("status", "未结账")\
                .single()\
                .execute()
            
            if not order_response.data:
                print("当前桌台暂无消费记录")
                return []
            
            order_id = order_response.data["order_id"]
            discount = order_response.data.get("discount", 1.0)
            
            # 获取订单明细
            items_response = supabase.table("order_items")\
                .select("order_item_id, dish_id, quantity, unit_price, subtotal, taste_choices, status")\
                .eq("order_id", order_id)\
                .order("created_at")\
                .execute()
            
            if not items_response.data:
                print("订单中暂无菜品")
                return []
            
            result = []
            total_amount = 0
            
            print("\n" + "="*80)
            print(f"聚香园 - 桌台 {self.current_table_number} 账单")
            print("="*80)
            print(f"{'菜品ID':<6} {'菜品名称':<10} {'数量':<4} {'单价':<6} {'小计':<6} {'状态':<6} {'口味':<30}")
            print("-"*80)
            
            for item in items_response.data:
                # 获取菜品名称
                dish_response = supabase.table("dishes")\
                    .select("dish_name")\
                    .eq("dish_id", item["dish_id"])\
                    .single()\
                    .execute()
                
                dish_name = dish_response.data["dish_name"] if dish_response.data else "未知菜品"
                
                # 获取退菜原因（如果有）
                refund_response = supabase.table("refund_records")\
                    .select("refund_reason")\
                    .eq("order_item_id", item["order_item_id"])\
                    .execute()
                
                refund_reason = refund_response.data[0]["refund_reason"] if refund_response.data else ""
                
                taste_str = json.dumps(item["taste_choices"], ensure_ascii=False)[:28] + "..." if len(json.dumps(item["taste_choices"], ensure_ascii=False)) > 30 else json.dumps(item["taste_choices"], ensure_ascii=False)
                refund_display = refund_reason[:8] + "..." if len(refund_reason) > 10 else refund_reason
                
                print(f"{item['order_item_id']:<6} {dish_name:<10} {item['quantity']:<4} {item['unit_price']:<6.2f} {item['subtotal']:<6.2f} {item['status']:<6} {taste_str:<30} {refund_display:<10}")
                
                if item["status"] != "已退菜":
                    total_amount += item["subtotal"]
                
                result.append({
                    **item,
                    "dish_name": dish_name,
                    "refund_reason": refund_reason
                })
            
            final_amount = total_amount * discount
            print("-"*80)
            print(f"{'':<6} {'':<10} {'':<4} {'':<6} {'折扣率':<6} {discount:<6.2f} {'':<30} {'':<10}")
            print(f"{'':<6} {'':<10} {'':<4} {'':<6} {'应付金额':<6} {final_amount:<6.2f} {'':<30} {'':<10}")
            print("="*80 + "\n")
            
            return result
        except Exception as e:
            print(f"查看账单失败：{str(e)}")
            return []

def test_connection() -> bool:
    """测试数据库连接"""
    try:
        response = supabase.table("roles").select("role_id").limit(1).execute()
        return True
    except Exception as e:
        print(f"数据库连接失败：{str(e)}")
        return False

def execute_sql(sql: str, params: dict = None):
    """执行SQL语句（支持查询/修改）"""
    if params is None:
        params = {}
    
    try:
        # 对于简单的查询，我们可以使用Supabase的查询方法
        # 这里我们只处理SELECT查询，其他操作通过存储过程或直接操作
        if sql.strip().upper().startswith("SELECT"):
            # 直接使用Supabase客户端执行简单查询
            # 注意：这种方法只适用于简单查询，复杂查询可能需要使用视图或存储过程
            table_match = ["tables", "users", "dishes", "orders", "order_items"]
            for table in table_match:
                if table in sql.lower():
                    response = supabase.table(table).select("*").execute()
                    return response.data
            
            # 如果没有匹配的表，返回空列表
            return []
        else:
            print(f"不支持的非SELECT查询: {sql}")
            return None
    except Exception as e:
        print(f"SQL执行失败：{str(e)}")
        return None

def call_procedure(proc_name: str, params: list = None):
    """调用存储过程"""
    if params is None:
        params = []
    
    try:
        # 将参数转换为字典格式
        params_dict = {}
        for i, param in enumerate(params):
            params_dict[f"p_{i+1}"] = param
        
        # 调用存储过程
        response = supabase.rpc(proc_name, params_dict).execute()
        return response.data
    except Exception as e:
        print(f"存储过程调用失败：{str(e)}")
        return None

# 初始化连接
if not test_connection():
    raise Exception("数据库连接失败，请检查配置")
print("数据库连接成功！")