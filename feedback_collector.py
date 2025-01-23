# 这是一个用于收集用户对Cursor使用反馈的增强版程序

import datetime  # 用于记录反馈时间

def collect_feedback():
    """
    收集用户对Cursor的反馈，包括评分和分类
    """
    print("欢迎使用Cursor反馈收集程序！")
    print("请告诉我们您对Cursor的使用体验。")
    
    # 获取用户评分
    while True:
        try:
            rating = int(input("请为Cursor的使用体验打分（1-5分）："))
            if 1 <= rating <= 5:
                break
            else:
                print("请输入1到5之间的整数。")
        except ValueError:
            print("请输入有效的数字。")
    
    # 获取反馈分类
    print("\n请选择反馈类型：")
    print("1. 功能建议")
    print("2. Bug报告")
    print("3. 使用体验")
    print("4. 其他")
    while True:
        try:
            category = int(input("请输入分类编号（1-4）："))
            if 1 <= category <= 4:
                break
            else:
                print("请输入1到4之间的整数。")
        except ValueError:
            print("请输入有效的数字。")
    
    # 获取用户反馈内容
    feedback = input("请输入您的具体反馈：")
    
    # 获取当前时间
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 将反馈、评分、分类和时间保存到文件中
    with open("feedback.txt", "a") as file:
        file.write(f"[{current_time}] 评分：{rating} 分类：{category} 反馈：{feedback}\n")
    
    print("感谢您的反馈！您的意见对我们非常重要。")

def show_feedback():
    """
    显示所有收集到的反馈
    """
    try:
        with open("feedback.txt", "r") as file:
            feedbacks = file.readlines()
            if feedbacks:
                print("\n所有收集到的反馈：")
                for feedback in feedbacks:
                    print(feedback.strip())
            else:
                print("目前还没有收集到任何反馈。")
    except FileNotFoundError:
        print("还没有收集到任何反馈。")

def show_statistics():
    """
    显示反馈的统计信息
    """
    try:
        with open("feedback.txt", "r") as file:
            feedbacks = file.readlines()
            if feedbacks:
                total_feedbacks = len(feedbacks)
                total_rating = 0
                for feedback in feedbacks:
                    # 提取评分
                    rating = int(feedback.split("评分：")[1].split()[0])
                    total_rating += rating
                average_rating = total_rating / total_feedbacks
                print(f"\n反馈统计：")
                print(f"总反馈数量：{total_feedbacks}")
                print(f"平均评分：{average_rating:.2f}")
            else:
                print("目前还没有收集到任何反馈。")
    except FileNotFoundError:
        print("还没有收集到任何反馈。")

def main():
    """
    主函数，程序的入口
    """
    while True:
        print("\n请选择操作：")
        print("1. 提供反馈")
        print("2. 查看所有反馈")
        print("3. 查看反馈统计")
        print("4. 退出")
        
        choice = input("请输入您的选择（1/2/3/4）：")
        
        if choice == '1':
            collect_feedback()
        elif choice == '2':
            show_feedback()
        elif choice == '3':
            show_statistics()
        elif choice == '4':
            print("感谢您的参与，再见！")
            break
        else:
            print("无效的选择，请输入1、2、3或4。")

if __name__ == "__main__":
    main() 