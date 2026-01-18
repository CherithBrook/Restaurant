import json
from db import supabase, call_procedure

class Chef:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.username = self._get_username()

    def _get_username(self) -> str:
        """获取用户名"""
        response = supabase.table("users").select("real_name").eq("user_id", self.user_id).single().execute()
        return response.data["real_name"] if response.data else "未知厨师"

    def view_order_list(self, category_name: str = None):
        """查看分单（按分类筛选）"""
        try:
            # 使用Supabase客户端直接查询视图
            query = supabase.from_("chef_order_view").select("*")
            if category_name:
                query = query.eq("category_name", category_name)
            
            query = query.order("sort_order").order("is_urgent", desc=True).order("created_at")
            response = query.execute()
            
            if not response.data:
                print(f"暂无{'[' + category_name + ']' if category_name else ''}未完成订单")
                return None
            
            # 按分类分组显示
            categories = {}
            for item in response.data:
                cat = item["category_name"]
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(item)
            
            print("\n" + "="*80)
            print(f"后厨分单 - 厨师：{self.username}")
            print("="*80)
            for cat, items in categories.items():
                print(f"\n【{cat}】")
                print("-"*80)
                print(f"{'订单号':<8} {'桌台号':<8} {'菜品名称':<12} {'数量':<4} {'催菜':<4} {'状态':<8} {'口味':<30} {'创建时间':<16}")
                print("-"*80)
                for item in items:
                    taste_str = json.dumps(item["taste_choices"], ensure_ascii=False)[:30]
                    urgent_str = "√" if item["is_urgent"] else "×"
                    create_time = item["created_at"].split("T")[0] + " " + item["created_at"].split("T")[1][:8]
                    print(f"{item['order_id']:<8} {item['table_number']:<8} {item['dish_name']:<12} {item['quantity']:<4} {urgent_str:<4} {item['status']:<8} {taste_str:<30} {create_time:<16}")
            print("="*80 + "\n")
            return response.data
        except Exception as e:
            print(f"查看分单失败：{str(e)}")
            return None

    def update_dish_status(self, order_item_id: int, new_status: str):
        """更新菜品制作状态（未制作/制作中/已完成）"""
        valid_status = ["未制作", "制作中", "已完成"]
        if new_status not in valid_status:
            print(f"无效状态：{new_status}，仅支持{valid_status}")
            return False
        
        result = call_procedure("update_dish_status", [order_item_id, new_status])
        if result is not None:
            print(f"更新成功！菜品ID：{order_item_id}，新状态：{new_status}")
            return True
        return False

# 示例用法
if __name__ == "__main__":
    chef = Chef(3)  # 用户ID=3（后厨）
    # 查看所有分单
    chef.view_order_list()
    # 查看热菜分单
    chef.view_order_list("热菜")
    # 更新菜品状态（假设订单明细ID=1为制作中）
    chef.update_dish_status(1, "制作中")
    # 再次查看分单
    chef.view_order_list("热菜")