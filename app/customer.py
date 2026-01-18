from db import get_conn

def choose_or_open_order():
    conn = get_conn()
    cur = conn.cursor()

    print("\n====== 桌台列表 ======")
    cur.execute("SELECT table_id, status FROM table_info ORDER BY table_id")
    tables = cur.fetchall()
    for t in tables:
        print(f"桌号 {t[0]} - {t[1]}")

    table_id = int(input("请选择桌号（空闲桌将自动开台）： "))

    cur.execute("""
        SELECT order_id FROM order_main
        WHERE table_id=%s AND status='未结算'
    """, (table_id,))
    row = cur.fetchone()

    if row:
        order_id = row[0]
        print(f"进入已有订单：{order_id}")
    else:
        cur.execute("SELECT p_open_table(%s)", (table_id,))
        order_id = cur.fetchone()[0]
        print(f"开台成功，新订单号：{order_id}")

    conn.commit()
    conn.close()
    return order_id


def show_menu():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT f.food_id, f.food_name, ft.type_name, f.price
        FROM food f
        JOIN food_type ft ON f.type_id = ft.type_id
        WHERE f.is_sale = TRUE
        ORDER BY f.food_id
    """)
    rows = cur.fetchall()
    conn.close()

    print("\n====== 菜单 ======")
    print("ID | 菜名 | 分类 | 价格")
    for r in rows:
        print(f"{r[0]} | {r[1]} | {r[2]} | {r[3]}")


def add_food():
    order_id = choose_or_open_order()
    show_menu()

    food_id = int(input("请选择菜品ID："))

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT t.taste_id, t.taste_name
        FROM food_taste ft
        JOIN taste_option t ON ft.taste_id = t.taste_id
        WHERE ft.food_id = %s
    """, (food_id,))
    tastes = cur.fetchall()

    if not tastes:
        print("该菜品无需口味选择")
        count = int(input("请输入数量："))
        cur.execute(
            "SELECT p_add_order_detail(%s,%s,NULL,%s)",
            (order_id, food_id, count)
        )
    else:
        print("可选口味：")
        for t in tastes:
            print(f"{t[0]} - {t[1]}")
        taste_id = int(input("请选择口味ID："))
        count = int(input("请输入数量："))
        cur.execute(
            "SELECT p_add_order_detail(%s,%s,%s,%s)",
            (order_id, food_id, taste_id, count)
        )

    conn.commit()
    conn.close()
    print("✅ 点餐 / 加菜成功")
