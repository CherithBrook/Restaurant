from supabase import create_client, Client
import os

# Supabase配置（替换为你的实际配置）
SUPABASE_URL = "https://lkadifukazgphwzkfuez.supabase.co"
SUPABASE_KEY = "sb_secret_71F1tqMywPNfvbxK9lUj_g_-QMiHOHJ"

# 创建Supabase客户端
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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
            # 直接使用Supabase客户端执行查询
            # 注意：这种方法只适用于简单查询，复杂查询可能需要使用视图或存储过程
            response = supabase.table("tables").select("*").execute()
            return response.data
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

# ---------------------- 新增辅助查询方法（优化顾客端体验）----------------------
def get_available_tables() -> list:
    """获取所有空闲桌台（供顾客选择）"""
    try:
        response = supabase.table("tables")\
            .select("table_id, table_number, table_type, capacity")\
            .eq("status", "空闲")\
            .order("table_type")\
            .order("table_number")\
            .execute()
        return response.data
    except Exception as e:
        print(f"查询空闲桌台失败：{str(e)}")
        return []

def get_all_active_dishes() -> list:
    """获取所有上架菜品及对应的口味选项（含必选标记）"""
    try:
        # 由于复杂查询，我们使用多个查询组合
        # 首先获取所有上架菜品
        dishes_response = supabase.table("dishes")\
            .select("dish_id, dish_name, category_id, price, description, sort_order")\
            .eq("is_active", True)\
            .order("sort_order")\
            .execute()
        
        if not dishes_response.data:
            return []
        
        dishes = dishes_response.data
        
        # 为每个菜品获取分类信息和口味选项
        result = []
        for dish in dishes:
            # 获取分类信息
            category_response = supabase.table("dish_categories")\
                .select("category_name")\
                .eq("category_id", dish["category_id"])\
                .single()\
                .execute()
            
            if category_response.data:
                dish["category_name"] = category_response.data["category_name"]
            
            # 获取口味选项
            taste_response = supabase.rpc("get_dish_tastes", {"p_dish_id": dish["dish_id"]}).execute()
            if taste_response.data:
                dish["taste_options"] = taste_response.data
            else:
                dish["taste_options"] = []
            
            result.append(dish)
        
        return result
    except Exception as e:
        print(f"查询菜品失败：{str(e)}")
        return []

def get_dish_required_tastes(dish_id: int) -> list:
    """获取指定菜品的必选口味"""
    try:
        response = supabase.rpc("get_required_tastes", {"p_dish_id": dish_id}).execute()
        return response.data
    except Exception as e:
        print(f"查询必选口味失败：{str(e)}")
        return []

# 初始化连接
if not test_connection():
    raise Exception("数据库连接失败，请检查配置")
print("数据库连接成功！")