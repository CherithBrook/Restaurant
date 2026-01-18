from customer import choose_or_open_order, add_food
from db import get_conn

def open_and_order():
    add_food()

def refund_food():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT d.detail_id, f.food_name, d.status
        FROM order_detail d
        JOIN food f ON d.food_id = f.food_id
        WHERE d.status <> '已退'
    """)
    rows = cur.fetchall()

    print("\n可退菜品：")
    for r in rows:
        print(f"{r[0]} - {r[1]} ({r[2]})")

    detail_id = int(input("请选择要退的明细ID："))
    reason = input("请输入退菜原因：")

    cur.execute(
        "SELECT p_refund_detail(%s,%s)",
        (detail_id, reason)
    )
    conn.commit()
    conn.close()
    print("✅ 退菜成功")

def checkout():
    order_id = choose_or_open_order()
    discount = float(input("请输入折扣（如 0.9）："))
    zero = float(input("请输入抹零金额："))

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT p_checkout(%s,%s,%s)",
        (order_id, discount, zero)
    )
    conn.commit()
    conn.close()
    print("✅ 结账完成")
