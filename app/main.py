import customer
import waiter
import chef
import manager

while True:
    print("\n====== 餐厅点餐系统 ======")
    print("1. 顾客")
    print("2. 服务员")
    print("3. 后厨")
    print("4. 经理")
    print("0. 退出")

    role = input("请选择角色：")

    if role == '1':
        customer.add_food()

    elif role == '2':
        print("\n1. 开台 / 点餐")
        print("2. 退菜")
        print("3. 结账")
        c = input("请选择操作：")

        if c == '1':
            waiter.open_and_order()
        elif c == '2':
            waiter.refund_food()
        elif c == '3':
            waiter.checkout()

    elif role == '3':
        chef.view_orders()
        chef.update_status()

    elif role == '4':
        manager.add_food()
        manager.view_revenue()

    elif role == '0':
        break
