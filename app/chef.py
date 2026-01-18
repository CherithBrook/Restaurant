from db import get_conn

def view_orders():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM v_chef_orders")
    rows = cur.fetchall()
    conn.close()

    print("\n====== 后厨分单 ======")
    for r in rows:
        print(f"明细ID:{r[0]} | {r[1]} | {r[2]} | 数量:{r[3]} | 状态:{r[4]} | 分类:{r[5]}")

def update_status():
    detail_id = int(input("请输入明细ID："))
    new_status = input("新状态（制作中 / 已完成）：")

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE order_detail SET status=%s WHERE detail_id=%s",
        (new_status, detail_id)
    )
    conn.commit()
    conn.close()
    print("✅ 状态已更新")
