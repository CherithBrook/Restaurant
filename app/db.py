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

# ---------------------- 新增辅助查询方法（优化顾客端体验）----------------------
def get_available_tables() -> list:
    """获取所有空闲桌台（供顾客选择）"""
    sql = """
    SELECT table_id, table_number, table_type, capacity 
    FROM tables 
    WHERE status = '空闲' 
    ORDER BY table_type, table_number
    """
    return execute_sql(sql)

def get_all_active_dishes() -> list:
    """获取所有上架菜品及对应的口味选项（含必选标记）"""
    sql = """
    SELECT 
        d.dish_id,
        d.dish_name,
        dc.category_name,
        d.price,
        d.description,
        json_agg(
            json_build_object(
                'taste_id', to_char(to, taste_id),
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
    return execute_sql(sql)

def get_dish_required_tastes(dish_id: int) -> list:
    """获取指定菜品的必选口味"""
    sql = """
    SELECT to.taste_id, to.taste_name
    FROM taste_options to
    JOIN dish_taste_mappings dtm ON to.taste_id = dtm.taste_id
    WHERE dtm.dish_id = %s AND dtm.is_required = TRUE
    """
    return execute_sql(sql, {"$1": dish_id})

# 初始化连接
if not test_connection():
    raise Exception("数据库连接失败，请检查配置")
print("数据库连接成功！")