#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主程序入口模块
职责：菜单循环、用户交互、程序入口
"""

import sys

from config import (
    COLOR_RESET, COLOR_GREEN, COLOR_CYAN, COLOR_BOLD,
    PAGE_SIZE, SUBJECTS, SCORE_MIN, SCORE_MAX, AGE_MIN, AGE_MAX
)
from utils import (
    print_title, print_success, print_error, print_warning, print_info,
    print_table, load_students_data, save_students_data
)
from validator import (
    validate_student_id, validate_name, validate_gender, normalize_gender,
    validate_age, validate_score, validate_class_name
)
from processor import StudentProcessor


def input_with_prompt(prompt: str, allow_empty: bool = False) -> str:
    """带提示的输入"""
    while True:
        try:
            value = input(f"{COLOR_CYAN}{prompt}{COLOR_RESET}").strip()
            if not value and not allow_empty:
                print_error("输入不能为空，请重新输入！")
                continue
            return value
        except (KeyboardInterrupt, EOFError):
            print_error("输入被中断")
            return ""


def input_int(prompt: str, min_val: int = None, max_val: int = None) -> int:
    """输入整数"""
    while True:
        try:
            value = input_with_prompt(prompt)
            num = int(value)
            if min_val is not None and num < min_val:
                print_error(f"输入不能小于 {min_val}")
                continue
            if max_val is not None and num > max_val:
                print_error(f"输入不能大于 {max_val}")
                continue
            return num
        except ValueError:
            print_error("请输入有效的整数！")


def input_score(prompt: str) -> int:
    """输入成绩"""
    return input_int(prompt, SCORE_MIN, SCORE_MAX)


def show_menu(processor: StudentProcessor):
    """显示主菜单"""
    print()
    print(f"{COLOR_CYAN}{'='*50}{COLOR_RESET}")
    print(f"{COLOR_BOLD}           学生成绩管理系统 v2.0{COLOR_RESET}")
    print(f"{COLOR_CYAN}{'='*50}{COLOR_RESET}")
    print(f"  当前学生数：{COLOR_GREEN}{len(processor.students)}{COLOR_RESET} 人")
    print(f"{COLOR_CYAN}{'='*50}{COLOR_RESET}")
    print()
    print("  1. 添加学生")
    print("  2. 删除学生")
    print("  3. 修改学生信息")
    print("  4. 查询学生")
    print("  5. 显示所有学生")
    print("  6. 成绩统计分析")
    print("  7. 按条件筛选")
    print("  8. 导入/导出数据")
    print("  9. 退出系统")
    print()
    print(f"{COLOR_CYAN}{'='*50}{COLOR_RESET}")


def menu_add_student(processor: StudentProcessor):
    """菜单：添加学生"""
    print_title("添加学生")
    
    # 输入学号
    while True:
        student_id = input_with_prompt("请输入学号（输入'自动'自动生成）：")
        
        if student_id == "自动":
            break
        
        is_valid, error = validate_student_id(student_id, processor.students)
        if is_valid:
            break
        print_error(error)
    
    # 输入基本信息
    name = input_with_prompt("请输入姓名：")
    while True:
        is_valid, error = validate_name(name)
        if is_valid:
            break
        print_error(error)
        name = input_with_prompt("请重新输入姓名：")
    
    gender = input_with_prompt("请输入性别（男/女）：")
    gender = normalize_gender(gender)
    
    age = input_int(f"请输入年龄（{AGE_MIN}-{AGE_MAX}）：", AGE_MIN, AGE_MAX)
    
    class_name = input_with_prompt("请输入班级（如：高一(1)班）：")
    
    # 输入成绩
    print_info("请输入各科成绩：")
    subjects_scores = {}
    for subject in SUBJECTS:
        score = input_score(f"  {subject}（{SCORE_MIN}-{SCORE_MAX}）：")
        subjects_scores[subject] = score
    
    # 添加学生
    success, message = processor.add_student(
        student_id, name, gender, age, class_name, subjects_scores
    )
    
    if success:
        print_success(message)
    else:
        print_error(message)


def menu_delete_student(processor: StudentProcessor):
    """菜单：删除学生"""
    print_title("删除学生")
    
    if not processor.students:
        print_warning("暂无学生数据")
        return
    
    print("删除方式：")
    print("  1. 按学号删除")
    print("  2. 按姓名删除（支持模糊匹配）")
    
    choice = input_with_prompt("请选择（1/2）：")
    
    if choice == "1":
        student_id = input_with_prompt("请输入学号：")
        success, message = processor.delete_student_by_id(student_id)
        
        if success:
            print_success(message)
        else:
            print_error(message)
    
    elif choice == "2":
        name = input_with_prompt("请输入姓名（支持模糊匹配）：")
        matched, message = processor.delete_students_by_name(name)
        
        if not matched:
            print_error("未找到匹配的学生")
            return
        
        print(f"\n找到 {len(matched)} 个匹配结果：")
        for i, student in enumerate(matched, 1):
            print(f"  {i}. {student['name']}（{student['id']}）")
        
        if len(matched) == 1:
            confirm = input_with_prompt("确认删除？(Y/N)：").upper()
            if confirm in ["Y", "是"]:
                success, message = processor.delete_student_by_id(matched[0]["id"])
                if success:
                    print_success(message)
            else:
                print_info("已取消")
        else:
            idx = input_int("请输入要删除的序号（0取消）：", 0, len(matched))
            if idx == 0:
                print_info("已取消")
                return
            
            confirm = input_with_prompt("确认删除？(Y/N)：").upper()
            if confirm in ["Y", "是"]:
                success, message = processor.delete_student_by_id(matched[idx - 1]["id"])
                if success:
                    print_success(message)
            else:
                print_info("已取消")
    else:
        print_error("无效选择")


def menu_modify_student(processor: StudentProcessor):
    """菜单：修改学生信息"""
    print_title("修改学生信息")
    
    if not processor.students:
        print_warning("暂无学生数据")
        return
    
    student_id = input_with_prompt("请输入要修改的学生学号：")
    student = processor.find_by_id(student_id)
    
    if not student:
        print_error("未找到该学生")
        return
    
    print(f"\n当前信息：")
    print(f"  学号：{student['id']}")
    print(f"  姓名：{student['name']}")
    print(f"  性别：{student['gender']}")
    print(f"  年龄：{student['age']}")
    print(f"  班级：{student['class']}")
    print("  成绩：")
    for subject, score in student['subjects'].items():
        print(f"    {subject}：{score}")
    
    print("\n修改选项：")
    print("  1. 修改姓名")
    print("  2. 修改性别")
    print("  3. 修改年龄")
    print("  4. 修改班级")
    print("  5. 修改成绩")
    print("  0. 取消")
    
    choice = input_with_prompt("请选择（0-5）：")
    updates = {}
    
    if choice == "1":
        updates["name"] = input_with_prompt("请输入新姓名：")
    elif choice == "2":
        updates["gender"] = input_with_prompt("请输入新性别（男/女）：")
    elif choice == "3":
        updates["age"] = input_int(f"请输入新年龄（{AGE_MIN}-{AGE_MAX}）：", AGE_MIN, AGE_MAX)
    elif choice == "4":
        updates["class"] = input_with_prompt("请输入新班级：")
    elif choice == "5":
        print("科目列表：")
        for i, subject in enumerate(SUBJECTS, 1):
            print(f"  {i}. {subject}（当前：{student['subjects'][subject]}）")
        
        subject_idx = input_int("请选择要修改的科目（1-5）：", 1, 5)
        subject = SUBJECTS[subject_idx - 1]
        new_score = input_score(f"请输入新的{subject}成绩：")
        
        new_subjects = student["subjects"].copy()
        new_subjects[subject] = new_score
        updates["subjects"] = new_subjects
    elif choice == "0":
        print_info("已取消")
        return
    else:
        print_error("无效选择")
        return
    
    success, message = processor.update_student(student_id, updates)
    
    if success:
        print_success(message)
    else:
        print_error(message)


def menu_query_student(processor: StudentProcessor):
    """菜单：查询学生"""
    print_title("查询学生")
    
    if not processor.students:
        print_warning("暂无学生数据")
        return
    
    print("查询方式：")
    print("  1. 按学号精确查询")
    print("  2. 按姓名模糊查询")
    
    choice = input_with_prompt("请选择（1/2）：")
    
    if choice == "1":
        student_id = input_with_prompt("请输入学号：")
        student = processor.get_student_with_rank(student_id)
        
        if student:
            display_student_detail(student)
        else:
            print_error("未找到该学生")
    
    elif choice == "2":
        name = input_with_prompt("请输入姓名（支持模糊匹配）：")
        matched = processor.find_by_name(name)
        
        if matched:
            print(f"\n找到 {len(matched)} 个匹配结果：\n")
            for student in matched:
                student_with_rank = processor.get_student_with_rank(student["id"])
                display_student_detail(student_with_rank)
                print()
        else:
            print_error("未找到匹配的学生")
    else:
        print_error("无效选择")


def display_student_detail(student: dict):
    """显示学生详细信息"""
    from config import COLOR_CYAN, COLOR_GREEN, COLOR_YELLOW
    
    print(f"{COLOR_CYAN}{'='*40}{COLOR_RESET}")
    print(f"  学号：{student['id']}")
    print(f"  姓名：{student['name']}")
    print(f"  性别：{student['gender']}")
    print(f"  年龄：{student['age']}")
    print(f"  班级：{student['class']}")
    print(f"  成绩：")
    for subject, score in student['subjects'].items():
        print(f"    {subject}：{score}")
    print(f"  总分：{COLOR_GREEN}{student['total']}{COLOR_RESET}")
    print(f"  平均分：{COLOR_GREEN}{student['average']}{COLOR_RESET}")
    print(f"  排名：{COLOR_YELLOW}第 {student.get('rank', 0)} 名{COLOR_RESET}")
    print(f"{COLOR_CYAN}{'='*40}{COLOR_RESET}")


def menu_display_all(processor: StudentProcessor):
    """菜单：显示所有学生"""
    print_title("所有学生列表")
    
    if not processor.students:
        print_warning("暂无学生数据")
        return
    
    total_pages = (len(processor.students) + PAGE_SIZE - 1) // PAGE_SIZE
    current_page = 1
    
    while True:
        page_students, current_page, total_pages = processor.get_paginated_students(current_page)
        
        print(f"\n第 {current_page}/{total_pages} 页（共 {len(processor.students)} 人）\n")
        
        # 准备表格数据
        headers = ["序号", "学号", "姓名", "班级", "总分", "平均分", "排名"]
        rows = []
        
        for i, student in enumerate(page_students, (current_page - 1) * PAGE_SIZE + 1):
            rows.append([
                i,
                student["id"],
                student["name"],
                student["class"],
                student["total"],
                student["average"],
                student["rank"]
            ])
        
        print_table(headers, rows, [4, 12, 10, 12, 8, 8, 6])
        
        if total_pages == 1:
            input("\n按回车键返回...")
            break
        
        print(f"\n导航：N-下一页，P-上一页，G-跳转，Q-返回")
        nav = input_with_prompt("请选择：", allow_empty=True).upper()
        
        if nav == "N":
            if current_page < total_pages:
                current_page += 1
            else:
                print_warning("已经是最后一页")
        elif nav == "P":
            if current_page > 1:
                current_page -= 1
            else:
                print_warning("已经是第一页")
        elif nav == "G":
            page = input_int(f"请输入页码（1-{total_pages}）：", 1, total_pages)
            current_page = page
        elif nav in ["Q", ""]:
            break


def menu_statistics(processor: StudentProcessor):
    """菜单：成绩统计分析"""
    print_title("成绩统计分析")
    
    if not processor.students:
        print_warning("暂无学生数据")
        return
    
    stats = processor.calculate_statistics()
    
    print(f"\n{COLOR_GREEN}{'='*50}{COLOR_RESET}")
    print(f"                 成绩统计分析报告")
    print(f"{COLOR_GREEN}{'='*50}{COLOR_RESET}\n")
    
    # 前5名
    print("【前5名】")
    headers = ["排名", "学号", "姓名", "班级", "总分", "平均分"]
    rows = []
    for i, student in enumerate(stats["top5"], 1):
        rows.append([i, student["id"], student["name"], student["class"], 
                    student["total"], student["average"]])
    print_table(headers, rows, [6, 12, 10, 12, 8, 8])
    
    # 后3名
    print("\n【后3名】")
    rows = []
    total_count = stats["total_count"]
    for i, student in enumerate(stats["bottom3"], total_count - 2):
        rows.append([i, student["id"], student["name"], student["class"], 
                    student["total"], student["average"]])
    print_table(headers, rows, [6, 12, 10, 12, 8, 8])
    
    # 各科目统计
    print("\n【各科目统计】")
    headers = ["科目", "平均分", "最高分", "最低分"]
    rows = []
    for subject in SUBJECTS:
        stat = stats["subject_stats"][subject]
        rows.append([subject, stat["average"], stat["max"], stat["min"]])
    print_table(headers, rows, [10, 10, 10, 10])
    
    # 班级整体统计
    print("\n【班级整体统计】")
    print(f"  总人数：{stats['total_count']} 人")
    print(f"  班级平均总分：{stats['class_average_total']} 分")
    print(f"  班级平均平均分：{stats['class_average_score']} 分")
    print(f"  最高总分：{max(s['total'] for s in processor.students)} 分")
    print(f"  最低总分：{min(s['total'] for s in processor.students)} 分")
    print(f"  及格率：{stats['passing_rate']}%")
    
    print(f"\n{COLOR_GREEN}{'='*50}{COLOR_RESET}\n")
    
    # 生成报告
    success, message = processor.generate_report()
    if success:
        print_success(f"{message}（已保存到 ./data/output/成绩分析报告.md）")
    else:
        print_warning(message)
    
    input("按回车键返回...")


def menu_filter(processor: StudentProcessor):
    """菜单：按条件筛选"""
    print_title("按条件筛选学生")
    
    if not processor.students:
        print_warning("暂无学生数据")
        return
    
    print("筛选条件：")
    print("  1. 平均分 ≥ 90 分（优秀）")
    print("  2. 平均分 ≥ 85 分（良好）")
    print("  3. 平均分 ≥ 80 分（中等）")
    print("  4. 平均分 ≥ 60 分（及格）")
    print("  5. 特定科目不及格")
    print("  6. 特定班级")
    print("  0. 返回")
    
    choice = input_with_prompt("请选择（0-6）：")
    
    filtered = []
    title = ""
    
    if choice == "1":
        filtered = processor.filter_students("average_above", threshold=90)
        title = "平均分 ≥ 90 分的学生"
    elif choice == "2":
        filtered = processor.filter_students("average_above", threshold=85)
        title = "平均分 ≥ 85 分的学生"
    elif choice == "3":
        filtered = processor.filter_students("average_above", threshold=80)
        title = "平均分 ≥ 80 分的学生"
    elif choice == "4":
        filtered = processor.filter_students("average_above", threshold=60)
        title = "平均分 ≥ 60 分的学生"
    elif choice == "5":
        print("科目列表：")
        for i, subject in enumerate(SUBJECTS, 1):
            print(f"  {i}. {subject}")
        subject_idx = input_int("请选择科目（1-5）：", 1, 5)
        subject = SUBJECTS[subject_idx - 1]
        filtered = processor.filter_students("subject_failing", subject=subject)
        title = f"{subject}不及格的学生"
    elif choice == "6":
        class_name = input_with_prompt("请输入班级名称（支持模糊匹配）：")
        filtered = processor.filter_students("class", class_name=class_name)
        title = f"班级包含 '{class_name}' 的学生"
    elif choice == "0":
        return
    else:
        print_error("无效选择")
        return
    
    print(f"\n【{title}】")
    print(f"共找到 {len(filtered)} 人\n")
    
    if filtered:
        headers = ["学号", "姓名", "班级", "总分", "平均分"]
        rows = [[s["id"], s["name"], s["class"], s["total"], s["average"]] 
                for s in filtered]
        print_table(headers, rows, [12, 10, 12, 8, 8])
    else:
        print_info("没有找到符合条件的学生")
    
    print()
    input("按回车键返回...")


def menu_import_export(processor: StudentProcessor):
    """菜单：导入导出"""
    print_title("导入/导出数据")
    
    print("  1. 从CSV文件导入学生")
    print("  2. 导出当前所有学生到CSV")
    print("  0. 返回")
    
    choice = input_with_prompt("请选择（0-2）：")
    
    if choice == "1":
        filename = input_with_prompt("请输入CSV文件名（位于 ./data/input/）：", allow_empty=True)
        if not filename:
            filename = "import.csv"
        
        count, message = processor.import_students(filename)
        if count > 0:
            print_success(message)
        else:
            print_warning(message)
    
    elif choice == "2":
        from config import EXPORT_FILENAME
        success, message = processor.export_students(EXPORT_FILENAME)
        if success:
            print_success(f"{message}（位于 ./data/output/）")
        else:
            print_error(message)
    
    elif choice == "0":
        return
    else:
        print_error("无效选择")


def check_and_import_legacy(processor: StudentProcessor):
    """检查并导入legacy数据"""
    from utils import read_legacy_data
    
    # 如果students.json为空且legacy.dat存在，则自动导入
    if not processor.students and read_legacy_data():
        print_info("检测到 legacy.dat 文件，正在初始化导入...")
        count, message = processor.import_from_legacy()
        if count > 0:
            print_success(message)
        else:
            print_warning("legacy.dat 导入失败或为空")


def main():
    """主函数"""
    # 初始化处理器
    processor = StudentProcessor()
    
    # 检查并导入legacy数据
    check_and_import_legacy(processor)
    
    # 主循环
    while True:
        try:
            show_menu(processor)
            choice = input_with_prompt("请输入选项（1-9）：")
            
            if choice == "1":
                menu_add_student(processor)
            elif choice == "2":
                menu_delete_student(processor)
            elif choice == "3":
                menu_modify_student(processor)
            elif choice == "4":
                menu_query_student(processor)
            elif choice == "5":
                menu_display_all(processor)
            elif choice == "6":
                menu_statistics(processor)
            elif choice == "7":
                menu_filter(processor)
            elif choice == "8":
                menu_import_export(processor)
            elif choice == "9":
                save_students_data(processor.students)
                print()
                print(f"{COLOR_GREEN}{'='*50}{COLOR_RESET}")
                print(f"{COLOR_GREEN}{'感谢使用，再见！':^50}{COLOR_RESET}")
                print(f"{COLOR_GREEN}{'='*50}{COLOR_RESET}")
                break
            else:
                print_error("无效选项，请重新输入！")
        
        except KeyboardInterrupt:
            print("\n")
            print_warning("操作被中断")
        except Exception as e:
            print_error(f"发生错误：{e}")


if __name__ == "__main__":
    main()
