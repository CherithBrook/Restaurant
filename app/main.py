from customer import Customer
from waiter import Waiter
from chef import Chef
from manager import Manager
import time

def print_menu():
    """显示主菜单"""
    print("="*50)
    print("          聚香园中餐厅数据库管理系统")
    print("="*50)
    print("请选择您的角色：")
    print("1. 顾客")
    print("2. 服务员")
    print("3. 后厨")
    print("4. 经理")
    print("0. 退出系统")
    print("="*50)

def customer_menu(customer: Customer):
    """优化后的顾客菜单"""
    while True:
        print("\n" + "-"*40)
        print(f"顾客端 - 欢迎您：{customer.username}")
        print(f"当前绑定桌台：{customer.current_table_number or '未绑定'}")
        print("-"*40)
        
        # 根据是否绑定桌台显示不同菜单
        if not customer.current_table_id:
            print("1. 查看空闲桌台并绑定")
            print("0. 返回上一级")
        else:
            print("1. 查看菜品并点餐")
            print("2. 催菜")
            print("3. 查看账单")
            print("4. 解除桌台绑定")
            print("0. 返回上一级")
        print("-"*40)
        
        choice = input("请输入操作编号：")
        
        # 未绑定桌台时的操作
        if not customer.current_table_id:
            if choice == "1":
                # 展示空闲桌台并选择绑定
                tables = customer.view_available_tables()
                if tables:
                    while True:
                        table_id_input = input("请输入要绑定的桌台ID（输入0取消）：")
                        if table_id_input == "0":
                            break
                        try:
                            table_id = int(table_id_input)
                            if customer.bind_table(table_id):
                                break
                        except ValueError:
                            print("输入错误！请输入数字类型的桌台ID")
            elif choice == "0":
                break
            else:
                print("无效操作，请重新输入！")
        
        # 已绑定桌台时的操作
        else:
            if choice == "1":
                # 展示所有菜品并点餐
                dishes = customer.view_all_dishes()
                if dishes:
                    while True:
                        dish_id_input = input("请输入要点的菜品ID（输入0取消点餐）：")
                        if dish_id_input == "0":
                            break
                        try:
                            dish_id = int(dish_id_input)
                            # 验证菜品是否存在
                            dish_exists = any(d["dish_id"] == dish_id for d in dishes)
                            if not dish_exists:
                                print("菜品ID不存在，请重新输入！")
                                continue
                            # 输入数量
                            while True:
                                quantity_input = input("请输入菜品数量（至少1份）：")
                                try:
                                    quantity = int(quantity_input)
                                    if quantity >= 1:
                                        break
                                    else:
                                        print("数量必须大于0，请重新输入！")
                                except ValueError:
                                    print("输入错误！请输入数字")
                            # 选择口味
                            taste_choices = customer.select_taste_options(dish_id)
                            # 提交订单
                            customer.place_order(dish_id, quantity, taste_choices)
                            # 是否继续点餐
                            continue_choice = input("是否继续点餐？（y/n）：")
                            if continue_choice.lower() != "y":
                                break
                        except ValueError:
                            print("输入错误！请输入数字类型的菜品ID")
            elif choice == "2":
                # 催菜（需从账单查看菜品ID）
                customer.view_bill()
                while True:
                    order_item_id_input = input("请输入要催的菜品ID（输入0取消）：")
                    if order_item_id_input == "0":
                        break
                    try:
                        order_item_id = int(order_item_id_input)
                        customer.urge_dish(order_item_id)
                        break
                    except ValueError:
                        print("输入错误！请输入数字类型的菜品ID")
            elif choice == "3":
                # 查看账单
                customer.view_bill()
            elif choice == "4":
                # 解除绑定
                customer.unbind_table()
            elif choice == "0":
                break
            else:
                print("无效操作，请重新输入！")
        
        time.sleep(1)

# 以下为原有其他角色菜单，保持不变
def waiter_menu(waiter: Waiter):
    """服务员菜单"""
    while True:
        print("\n" + "-"*30)
        print(f"服务员端 - 欢迎您：{waiter.username}")
        print("-"*30)
        print("1. 查看桌台状态")
        print("2. 开台")
        print("3. 代客点餐/加菜")
        print("4. 退菜")
        print("5. 结账")
        print("0. 返回上一级")
        print("-"*30)
        choice = input("请输入操作编号：")
        if choice == "1":
            waiter.view_table_status()
        elif choice == "2":
            table_number = input("请输入桌台号：")
            waiter.open_table(table_number)
        elif choice == "3":
            table_number = input("请输入桌台号：")
            # 简化菜品选择
            print("菜品列表：")
            print("1. 水煮肉片(48元)  2. 麻婆豆腐(28元)  3. 拍黄瓜(16元)")
            dish_id = input("请输入菜品ID：")
            quantity = input("请输入数量：")
            taste_choices = {}
            if dish_id == "1":
                print("辣度：1-微辣 2-中辣 3-特辣")
                spice = input("请选择辣度：")
                print("用油量：4-少油 5-正常油")
                oil = input("请选择用油量：")
                taste_choices = {spice: {"1":"微辣","2":"中辣","3":"特辣"}[spice], oil: {"4":"少油","5":"正常油"}[oil]}
            dish_list = [{"dish_id": int(dish_id), "quantity": int(quantity), "taste_choices": taste_choices}]
            waiter.place_order_for_customer(table_number, dish_list)
        elif choice == "4":
            order_item_id = input("请输入菜品ID：")
            reason = input("请输入退菜原因：")
            waiter.refund_dish(int(order_item_id), reason)
        elif choice == "5":
            table_number = input("请输入桌台号：")
            discount = input("请输入折扣率（0-1，默认1.0）：") or 1.0
            waiter.settle_bill(table_number, float(discount))
        elif choice == "0":
            break
        else:
            print("无效操作，请重新输入！")
        time.sleep(1)

def chef_menu(chef: Chef):
    """后厨菜单"""
    while True:
        print("\n" + "-"*30)
        print(f"后厨端 - 欢迎您：{chef.username}")
        print("-"*30)
        print("1. 查看所有分单")
        print("2. 查看分类分单")
        print("3. 更新菜品状态")
        print("0. 返回上一级")
        print("-"*30)
        choice = input("请输入操作编号：")
        if choice == "1":
            chef.view_order_list()
        elif choice == "2":
            category = input("请输入分类名称（热菜/凉菜/汤羹/主食/酒水）：")
            chef.view_order_list(category)
        elif choice == "3":
            order_item_id = input("请输入菜品ID：")
            print("状态选项：1-未制作 2-制作中 3-已完成")
            status_choice = input("请选择新状态编号：")
            status_map = {"1":"未制作", "2":"制作中", "3":"已完成"}
            if status_choice in status_map:
                chef.update_dish_status(int(order_item_id), status_map[status_choice])
            else:
                print("无效状态编号！")
        elif choice == "0":
            break
        else:
            print("无效操作，请重新输入！")
        time.sleep(1)

def manager_menu(manager: Manager):
    """经理菜单"""
    while True:
        print("\n" + "-"*30)
        print(f"经理端 - 欢迎您：{manager.username}")
        print("-"*30)
        print("1. 菜品管理（查看/添加/下架）")
        print("2. 桌台管理")
        print("3. 营收统计")
        print("0. 返回上一级")
        print("-"*30)
        choice = input("请输入操作编号：")
        if choice == "1":
            print("\n菜品管理子菜单：")
            print("1-查看菜品  2-添加菜品  3-下架菜品")
            sub_choice = input("请输入操作编号：")
            if sub_choice == "1":
                manager.view_dishes()
            elif sub_choice == "2":
                name = input("请输入菜品名称：")
                print("分类列表：1-热菜 2-凉菜 3-汤羹 4-主食 5-酒水")
                category_id = input("请输入分类ID：")
                price = input("请输入菜品价格：")
                desc = input("请输入菜品描述（可选）：")
                manager.add_dish(name, int(category_id), float(price), desc)
            elif sub_choice == "3":
                dish_id = input("请输入要下架的菜品ID：")
                manager.delete_dish(int(dish_id))
        elif choice == "2":
            manager.manage_tables()
        elif choice == "3":
            start = input("请输入开始日期（格式：YYYY-MM-DD，默认全部）：")
            end = input("请输入结束日期（格式：YYYY-MM-DD，默认全部）：")
            if start and end:
                manager.view_revenue(start, end)
            else:
                manager.view_revenue()
        elif choice == "0":
            break
        else:
            print("无效操作，请重新输入！")
        time.sleep(1)

if __name__ == "__main__":
    """程序入口"""
    while True:
        print_menu()
        role_choice = input("请输入角色编号：")
        
        if role_choice == "1":
            # 顾客（默认用户ID=1）
            customer = Customer(1)
            customer_menu(customer)
        elif role_choice == "2":
            # 服务员（默认用户ID=2）
            waiter = Waiter(2)
            waiter_menu(waiter)
        elif role_choice == "3":
            # 后厨（默认用户ID=3）
            chef = Chef(3)
            chef_menu(chef)
        elif role_choice == "4":
            # 经理（默认用户ID=4）
            manager = Manager(4)
            manager_menu(manager)
        elif role_choice == "0":
            print("感谢使用，再见！")
            break
        else:
            print("无效角色编号，请重新输入！")
        time.sleep(1)