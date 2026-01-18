import json
from db import supabase, call_procedure

class Waiter:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.username = self._get_username()

    def _get_username(self) -> str:
        """获取用户名"""
        response = supabase.table("users").select("real_name").eq("user_id", self.user_id).single().execute()
        return response.data["real_name"] if response.data else "未知服务员"

    def open_table(self, table_number: str) -> int:
        """开台"""
        # 获取table_id
        table_response = supabase.table("tables").select("table_id", "status").eq("table_number", table_number).single().execute()
        if not table_response.data:
            print(f"桌台{table_number}不存在！")
            return -1
        table_id = table_response.data["table_id"]
        if table_response.data["status"] != "空闲":
            print(f"桌台{table_number}当前状态为{table_response.data['status']}，无法开台")
            return -1

        # 调用开台存储过程
        result = call_procedure("open_table", [table_id, self.user_id])
        if result:
            order_id = result[0]["p_order_id"]
            print(f"开台成功！桌台：{table_number}，订单ID：{order_id}")
            return order_id
        return None

    def place_order_for_customer(self, table_number: str, dish_list: list):
        """代客点餐/加菜"""
        # 获取table_id
        table_response = supabase.table("tables").select("table_id").eq("table_number", table_number).single().execute()
        if not table_response.data:
            print(f"桌台{table_number}不存在！")
            return None
        table_id = table_response.data["table_id"]

        # 调用点餐存储过程
        dish_list_json = json.dumps(dish_list)
        result = call_procedure("place_order", [table_id, self.user_id, dish_list_json])
        if result:
            order_id = result[0]["p_order_id"]
            print(f"代客点餐成功！订单ID：{order_id}")
            return order_id
        return None

    def refund_dish(self, order_item_id: int, refund_reason: str):
        """退菜"""
        result = call_procedure("refund_dish", [order_item_id, refund_reason, self.user_id])
        if result is not None:
            print(f"退菜成功！菜品ID：{order_item_id}，原因：{refund_reason}")
            return True
        return False

    def settle_bill(self, table_number: str, discount: float = 1.0) -> float:
        """结账"""
        # 获取table_id
        table_response = supabase.table("tables").select("table_id").eq("table_number", table_number).single().execute()
        if not table_response.data:
            print(f"桌台{table_number}不存在！")
            return -1
        table_id = table_response.data["table_id"]

        # 调用结账存储过程
        result = call_procedure("settle_bill", [table_id, discount])
        if result is not None:
            # 获取结账后的订单总金额
            order_response = supabase.table("orders")\
                .select("total_amount")\
                .eq("table_id", table_id)\
                .eq("status", "已结账")\
                .order("created_at", desc=True)\
                .limit(1)\
                .single()\
                .execute()
            
            if order_response.data:
                total_amount = order_response.data["total_amount"]
                print(f"结账成功！桌台：{table_number}，应收金额：{total_amount:.2f}元")
                return total_amount
        return -1

    def view_table_status(self):
        """查看所有桌台状态"""
        response = supabase.table("tables").select("table_id", "table_number", "table_type", "capacity", "status").order("table_number").execute()
        if not response.data:
            print("暂无桌台数据")
            return None
        
        print("\n" + "="*60)
        print("聚香园桌台状态汇总")
        print("="*60)
        print(f"{'桌台号':<8} {'类型':<8} {'容量':<4} {'状态':<8}")
        print("-"*60)
        for table in response.data:
            print(f"{table['table_number']:<8} {table['table_type']:<8} {table['capacity']:<4} {table['status']:<8}")
        print("="*60 + "\n")
        return response.data

# 示例用法
if __name__ == "__main__":
    waiter = Waiter(2)  # 用户ID=2（服务员）
    waiter.view_table_status()
    # 开台
    waiter.open_table("T002")
    # 代客点餐
    dish_list = [
        {
            "dish_id": 2,
            "quantity": 1,
            "taste_choices": {"2": "中辣", "5": "正常油"}
        },
        {
            "dish_id": 9,
            "quantity": 2,
            "taste_choices": {}
        }
    ]
    waiter.place_order_for_customer("T002", dish_list)
    # 退菜（假设订单明细ID=5）
    waiter.refund_dish(5, "顾客不想吃了")
    # 结账（88折）
    waiter.settle_bill("T002", 0.88)