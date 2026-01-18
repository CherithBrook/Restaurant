from db import get_conn

def add_food():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT type_id, type_name FROM food_type")
    types = cur.fetchall()

    print("菜品分类：")
    for t in types:
        print(f"{t[0]} - {t[1]}")

    name = input("菜名：")
    type_id = int(input("分类ID："))
    price = float(input("价格："))

    cur.execute(
        "INSERT INTO food(food_name, type_id, price) VALUES(%s,%s,%s)",
        (name, type_id, price)
    )
    conn.commit()
    conn.close()
    print("✅ 菜品新增成功")

def view_revenue():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM v_manager_revenue")
    rows = cur.fetchall()
    conn.close()

    print("\n日期 | 营收")
    for r in rows:
        print(r)
