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
        sql = """
        SELECT table_id, table_number, table_type, capacity 
        FROM tables 
        WHERE status = '空闲' 
        ORDER BY table_type, table_number
        """
        result = execute_sql(sql)
        if not result:
            print("暂无空闲桌台")
            return []
        
        print("\n" + "="*50)
        print("聚香园 - 空闲桌台列表")
        print("="*50)
        print(f"{'桌台ID':<6} {'桌台号':<8} {'类型':<8} {'容量':<4}")
        print("-"*50)
        for table in result:
            print(f"{table['table_id']:<6} {table['table_number']:<8} {table['table_type']:<8} {table['capacity']:<4}")
        print("="*50 + "\n")
        return result
    
    def bind_table(self, table_id: int) -> bool:
        """绑定桌台（开台）"""
        try:
            # 检查桌台是否空闲
            table_response = supabase.table("tables").select("table_id", "table_number", "status").eq("table_id", table_id).single().execute()
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
        sql = """
        SELECT 
            d.dish_id,
            d.dish_name,
            dc.category_name,
            d.price,
            d.description,
            json_agg(
                json_build_object(
                    'taste_id', to.taste_id,
                    'taste_name', to.taste_name,
                    'is_required', dtm.is_required
                )
            ) AS taste_options
        FROM dishes d
        JOIN dish_categories dc ON d.category_id = dc.category_id
        LEFT JOIN dish_taste_mappings dtm ON d.dish_id = dtm.dish_id
        LEFT JOIN taste_options to ON dtm.taste_id = to.taste_id
        WHERE d.is_active = TRUE
        GROUP BY d.dish_id, dc.category_name
        ORDER BY dc.sort_order, d.sort_order
        """
        result = execute_sql(sql)
        if not result:
            print("暂无上架菜品")
            return []
        
        print("\n" + "="*80)
        print("聚香园 - 菜品列表")
        print("="*80)
        print(f"{'菜品ID':<6} {'菜品名称':<10} {'分类':<6} {'价格':<6} {'描述':<30} {'口味选项':<30}")
        print("-"*80)
        for dish in result:
            taste_info = []
            required_tastes = []
            optional_tastes = []
            
            for taste in dish["taste_options"]:
                if taste["is_required"]:
                    required_tastes.append(f"{taste['taste_id']}:{taste['taste_name']}(必选)")
                else:
                    optional_tastes.append(f"{taste['taste_id']}:{taste['taste_name']}(可选)")
            
            if required_tastes:
                taste_info.extend(required_tastes)
            if optional_tastes:
                taste_info.extend(optional_tastes)
            
            taste_str = " | ".join(taste_info)[:28] + "..." if len(" | ".join(taste_info)) > 30 else " | ".join(taste_info)
            desc = dish["description"][:28] + "..." if dish["description"] and len(dish["description"]) > 30 else dish["description"] or ""
            print(f"{dish['dish_id']:<6} {dish['dish_name']:<10} {dish['category_name']:<6} {dish['price']:<6.2f} {desc:<30} {taste_str:<30}")
        print("="*80 + "\n")
        return result
    
    def get_dish_required_tastes(self, dish_id: int) -> list:
        """获取指定菜品的必选口味"""
        sql = """
        SELECT to.taste_id, to.taste_name
        FROM taste_options to
        JOIN dish_taste_mappings dtm ON to.taste_id = dtm.taste_id
        WHERE dtm.dish_id = %s AND dtm.is_required = TRUE
        """
        return execute_sql(sql, {"$1": dish_id})
    
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
        sql = """
        SELECT to.taste_id, to.taste_name, dtm.is_required
        FROM taste_options to
        JOIN dish_taste_mappings dtm ON to.taste_id = dtm.taste_id
        WHERE dtm.dish_id = %s
        """
        return execute_sql(sql, {"$1": dish_id})
    
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
            sql = """
            SELECT oi.order_item_id
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            WHERE oi.order_item_id = %s AND o.table_id = %s
            """
            result = execute_sql(sql, {"$1": order_item_id, "$2": self.current_table_id})
            if not result:
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
        
        sql = """
        SELECT 
            oi.order_item_id,
            d.dish_name,
            oi.quantity,
            oi.unit_price,
            oi.subtotal,
            oi.taste_choices,
            oi.status,
            COALESCE(rr.refund_reason, '') AS refund_reason,
            o.discount,
            o.total_amount
        FROM 
            orders o
        JOIN order_items oi ON o.order_id = oi.order_item_id
        JOIN dishes d ON oi.dish_id = d.dish_id
        LEFT JOIN refund_records rr ON oi.order_item_id = rr.order_item_id
        WHERE 
            o.table_id = %s AND o.status = '未结账'
        ORDER BY 
            oi.created_at
        """
        result = execute_sql(sql, {"$1": self.current_table_id})
        if not result:
            print("当前桌台暂无消费记录")
            return []
        
        print("\n" + "="*80)
        print(f"聚香园 - 桌台 {self.current_table_number} 账单")
        print("="*80)
        print(f"{'菜品ID':<6} {'菜品名称':<10} {'数量':<4} {'单价':<6} {'小计':<6} {'状态':<6} {'口味':<30} {'退菜原因':<10}")
        print("-"*80)
        
        total_amount = 0
        discount = result[0]["discount"]
        
        for item in result:
            taste_str = json.dumps(item["taste_choices"], ensure_ascii=False)[:28] + "..." if len(json.dumps(item["taste_choices"], ensure_ascii=False)) > 30 else json.dumps(item["taste_choices"], ensure_ascii=False)
            refund_reason = item["refund_reason"][:8] + "..." if len(item["refund_reason"]) > 10 else item["refund_reason"]
            print(f"{item['order_item_id']:<6} {item['dish_name']:<10} {item['quantity']:<4} {item['unit_price']:<6.2f} {item['subtotal']:<6.2f} {item['status']:<6} {taste_str:<30} {refund_reason:<10}")
            
            if item["status"] != "已退菜":
                total_amount += item["subtotal"]
        
        final_amount = total_amount * discount
        print("-"*80)
        print(f"{'':<6} {'':<10} {'':<4} {'':<6} {'折扣率':<6} {discount:<6.2f} {'':<30} {'':<10}")
        print(f"{'':<6} {'':<10} {'':<4} {'':<6} {'应付金额':<6} {final_amount:<6.2f} {'':<30} {'':<10}")
        print("="*80 + "\n")
        
        return result

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
        response = supabase.rpc("exec_sql", {"sql": sql, "params": params}).execute()
        return response.data
    except Exception as e:
        print(f"SQL执行失败：{str(e)}")
        return None

def call_procedure(proc_name: str, params: list = None):
    """调用存储过程"""
    if params is None:
        params = []
    try:
        response = supabase.rpc(proc_name, dict(zip([f"p_{i}" for i in range(len(params))], params))).execute()
        return response.data
    except Exception as e:
        print(f"存储过程调用失败：{str(e)}")
        return None

# 初始化连接
if not test_connection():
    raise Exception("数据库连接失败，请检查配置")
print("数据库连接成功！")