import json
from db import supabase, execute_sql

class Manager:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.username = self._get_username()

    def _get_username(self) -> str:
        """获取用户名"""
        response = supabase.table("users").select("real_name").eq("user_id", self.user_id).single().execute()
        return response.data["real_name"] if response.data else "未知经理"

    # 菜品管理
    def view_dishes(self, category_id: int = None):
        """查看菜品列表"""
        try:
            # 使用Supabase客户端直接查询
            query = supabase.table("dishes").select("""
                dish_id, dish_name, category_id, price, description, is_active, sort_order,
                dish_categories!inner(category_name)
            """)
            
            if category_id:
                query = query.eq("category_id", category_id)
            
            query = query.order("sort_order")
            response = query.execute()
            
            result = response.data
            if not result:
                print("暂无菜品数据")
                return None
            
            print("\n" + "="*70)
            print(f"菜品管理 - 经理：{self.username}")
            print("="*70)
            print(f"{'菜品ID':<6} {'菜品名称':<12} {'分类':<6} {'价格':<8} {'状态':<6} {'排序':<4} {'描述':<30}")
            print("-"*70)
            for dish in result:
                status = "上架" if dish.get("is_active", True) else "下架"
                desc = dish.get("description", "")[:30] if dish.get("description") else ""
                category_name = dish.get("dish_categories", {}).get("category_name", "未知") if dish.get("dish_categories") else "未知"
                price = dish.get("price", 0.0)
                print(f"{dish['dish_id']:<6} {dish['dish_name']:<12} {category_name:<6} {price:<8.2f} {status:<6} {dish.get('sort_order', 0):<4} {desc:<30}")
            print("="*70 + "\n")
            return result
        except Exception as e:
            print(f"查询菜品失败：{str(e)}")
            return None

    def add_dish(self, dish_name: str, category_id: int, price: float, description: str = "", sort_order: int = 0):
        """添加新菜品（修复查询结果为空的处理）"""
        try:
            # 检查菜品是否已存在（使用execute()而非single()，避免无结果时抛出异常）
            exists_response = supabase.table("dishes").select("dish_id").eq("dish_name", dish_name).execute()
            if exists_response.data:
                print(f"菜品 {dish_name} 已存在，无法重复添加")
                return False
            
            # 插入菜品
            response = supabase.table("dishes").insert({
                "dish_name": dish_name,
                "category_id": category_id,
                "price": price,
                "description": description,
                "sort_order": sort_order,
                "is_active": True
            }).execute()
            
            if response.data:
                dish_id = response.data[0]["dish_id"]
                print(f"添加成功！菜品ID：{dish_id}，菜品名称：{dish_name}")
                return dish_id
            return False
        except Exception as e:
            print(f"添加菜品失败：{str(e)}")
            return False

    def delete_dish(self, dish_id: int):
        """下架菜品（逻辑删除）"""
        response = supabase.table("dishes").update({"is_active": False}).eq("dish_id", dish_id).execute()
        if response.count > 0:
            print(f"下架成功！菜品ID：{dish_id}")
            return True
        print(f"下架失败！菜品ID：{dish_id} 不存在或已下架")
        return False

    # 桌台管理
    def manage_tables(self, table_number: str = None):
        """查看/更新桌台信息"""
        # 查看桌台
        try:
            query = supabase.table("tables").select("*")
            if table_number:
                query = query.eq("table_number", table_number)
            query = query.order("table_number")
            response = query.execute()
            
            result = response.data
            if not result:
                print("暂无桌台数据")
                return None
            
            print("\n" + "="*60)
            print(f"桌台管理 - 经理：{self.username}")
            print("="*60)
            print(f"{'桌台ID':<6} {'桌台号':<8} {'类型':<8} {'容量':<4} {'状态':<8} {'创建时间':<16}")
            print("-"*60)
            for table in result:
                create_time = table["created_at"].split("T")[0] + " " + table["created_at"].split("T")[1][:8]
                print(f"{table['table_id']:<6} {table['table_number']:<8} {table['table_type']:<8} {table['capacity']:<4} {table['status']:<8} {create_time:<16}")
            print("="*60 + "\n")
            return result
        except Exception as e:
            print(f"查询桌台失败：{str(e)}")
            return None

    # 营收统计
    def view_revenue(self, start_date: str = None, end_date: str = None):
        """查看营收统计（按日期范围）"""
        try:
            # 使用 revenue_view 视图
            query = supabase.from_("revenue_view").select("*")
            
            if start_date and end_date:
                query = query.gte("business_date", start_date).lte("business_date", end_date)
            elif start_date:
                query = query.gte("business_date", start_date)
            elif end_date:
                query = query.lte("business_date", end_date)
            
            query = query.order("business_date", desc=True).order("sort_order")
            response = query.execute()
            
            result = response.data
            if not result:
                print("暂无营收数据")
                return None
            
            # 按日期分组统计
            dates = {}
            total_revenue = 0.0
            for item in result:
                date_str = item["business_date"]
                if date_str not in dates:
                    dates[date_str] = {"items": [], "total": 0.0}
                dates[date_str]["items"].append(item)
                dates[date_str]["total"] += item.get("net_amount", 0.0)
                total_revenue += item.get("net_amount", 0.0)
            
            print("\n" + "="*80)
            print(f"营收统计 - 经理：{self.username}")
            print(f"统计范围：{'所有日期' if not start_date else f'{start_date} 至 {end_date}'}")
            print("="*80)
            for date, data in dates.items():
                print(f"\n【{date}】 - 当日总营收：{data['total']:.2f}元")
                print("-"*80)
                print(f"{'分类':<8} {'订单数':<6} {'菜品数':<6} {'毛收入':<10} {'净收入':<10} {'使用桌台数':<8}")
                print("-"*80)
                for item in data["items"]:
                    print(f"{item['category_name']:<8} {item.get('order_count', 0):<6} {item.get('item_count', 0):<6} {item.get('gross_amount', 0.0):<10.2f} {item.get('net_amount', 0.0):<10.2f} {item.get('table_count', 0):<8}")
            print("\n" + "="*80)
            print(f"累计总营收：{total_revenue:.2f}元")
            print("="*80 + "\n")
            return result
        except Exception as e:
            print(f"查询营收数据失败：{str(e)}")
            return None

# 示例用法
if __name__ == "__main__":
    manager = Manager(4)  # 用户ID=4（经理）
    # 查看菜品
    manager.view_dishes()
    # 添加菜品
    manager.add_dish("鱼香肉丝", 1, 38.00, "经典川菜，酸甜可口", 3)
    # 下架菜品（假设菜品ID=11）
    manager.delete_dish(11)
    # 查看桌台
    manager.manage_tables()
    # 查看营收（近7天）
    manager.view_revenue("2026-01-01", "2026-01-18")