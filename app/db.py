from supabase import create_client, Client
import os
from datetime import datetime

# Supabase配置（建议改为环境变量）
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
    """执行SQL语句（支持查询/修改）- 修复版"""
    try:
        if sql.strip().upper().startswith("SELECT"):
            import re
            # 提取表名（简化处理）
            table_match = re.search(r'FROM\s+(\w+)', sql, re.IGNORECASE)
            if table_match:
                table_name = table_match.group(1)
                # 如果是视图
                if '_view' in table_name.lower():
                    return supabase.from_(table_name).select("*").execute().data
                # 普通表
                else:
                    return supabase.table(table_name).select("*").execute().data
            
            # 视图查询
            view_match = re.search(r'FROM\s+(\w+_view)', sql, re.IGNORECASE)
            if view_match:
                view_name = view_match.group(1)
                return supabase.from_(view_name).select("*").execute().data
            
            # 其他复杂查询
            print(f"复杂查询建议使用视图或存储过程: {sql[:100]}...")
            return []
        else:
            print(f"非SELECT查询建议使用相应方法: {sql[:100]}...")
            return None
    except Exception as e:
        print(f"SQL执行失败：{str(e)}")
        return None

def call_procedure(proc_name: str, params: list = None):
    """调用存储过程 - 修复版（修正参数映射顺序和名称）"""
    if params is None:
        params = []
    
    try:
        # 构建参数字典（严格匹配存储过程定义的参数顺序和名称）
        params_dict = {}
        
        if proc_name == "open_table":
            # 存储过程定义：p_table_id, p_created_by, OUT p_order_id
            if len(params) >= 2:
                params_dict["p_table_id"] = params[0]
                params_dict["p_created_by"] = params[1]
        elif proc_name == "place_order":
            # 存储过程定义：p_table_id, p_created_by, p_dish_list, OUT p_order_id
            if len(params) >= 3:
                params_dict["p_table_id"] = params[0]
                params_dict["p_created_by"] = params[1]
                params_dict["p_dish_list"] = params[2]
        elif proc_name == "settle_bill":
            # 存储过程定义：p_table_id, p_discount
            if len(params) >= 2:
                params_dict["p_table_id"] = params[0]
                params_dict["p_discount"] = params[1]
        elif proc_name == "refund_dish":
            # 存储过程定义：p_order_item_id, p_refund_reason, p_refunded_by
            if len(params) >= 3:
                params_dict["p_order_item_id"] = params[0]
                params_dict["p_refund_reason"] = params[1]
                params_dict["p_refunded_by"] = params[2]
        elif proc_name == "urge_dish":
            # 存储过程定义：p_order_item_id
            if len(params) >= 1:
                params_dict["p_order_item_id"] = params[0]
        elif proc_name == "update_dish_status":
            # 存储过程定义：p_order_item_id, p_new_status
            if len(params) >= 2:
                params_dict["p_order_item_id"] = params[0]
                params_dict["p_new_status"] = params[1]
        else:
            # 通用参数映射
            for i, param in enumerate(params):
                params_dict[f"p{i+1}"] = param
        
        # 调用存储过程
        response = supabase.rpc(proc_name, params_dict).execute()
        return response.data
    except Exception as e:
        print(f"存储过程调用失败：{str(e)}")
        return None

# ---------------------- 辅助查询方法 ----------------------
def get_available_tables() -> list:
    """获取所有空闲桌台"""
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
    """获取所有上架菜品及对应的口味选项"""
    try:
        # 获取菜品
        dishes_response = supabase.table("dishes")\
            .select("dish_id, dish_name, category_id, price, description, sort_order")\
            .eq("is_active", True)\
            .order("sort_order")\
            .execute()
        
        if not dishes_response.data:
            return []
        
        dishes = dishes_response.data
        
        # 获取分类信息
        for dish in dishes:
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
            if taste_response.data:
                dish["taste_options"] = taste_response.data
            else:
                dish["taste_options"] = []
        
        return dishes
    except Exception as e:
        print(f"查询菜品失败：{str(e)}")
        return []

def get_dish_with_tastes(dish_id: int) -> dict:
    """获取菜品详情（含口味选项）"""
    try:
        # 获取菜品基本信息
        dish_response = supabase.table("dishes")\
            .select("*")\
            .eq("dish_id", dish_id)\
            .single()\
            .execute()
        
        if not dish_response.data:
            return None
        
        dish = dish_response.data
        
        # 获取分类名
        category_response = supabase.table("dish_categories")\
            .select("category_name")\
            .eq("category_id", dish["category_id"])\
            .single()\
            .execute()
        
        dish["category_name"] = category_response.data["category_name"] if category_response.data else "未知分类"
        
        # 获取口味选项
        taste_response = supabase.rpc("get_dish_tastes", {"p_dish_id": dish_id}).execute()
        dish["taste_options"] = taste_response.data if taste_response.data else []
        
        return dish
    except Exception as e:
        print(f"获取菜品详情失败：{str(e)}")
        return None

# 初始化连接
if not test_connection():
    raise Exception("数据库连接失败，请检查配置")
print("数据库连接成功！")