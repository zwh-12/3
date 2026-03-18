#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具函数模块
职责：提供文件读写、表格打印、颜色输出、计算辅助等通用工具函数
"""

import os
import json
import csv
from typing import List, Dict, Any, Optional

# 导入配置
from config import (
    COLOR_RESET, COLOR_RED, COLOR_GREEN, COLOR_YELLOW,
    COLOR_BLUE, COLOR_CYAN, COLOR_BOLD,
    DATA_DIR, OUTPUT_DIR, STUDENTS_FILE, CSV_ENCODING, SUBJECTS
)


# =============================================
# 颜色输出函数
# =============================================

def print_title(title: str):
    """打印带颜色的标题"""
    print(f"\n{COLOR_CYAN}{COLOR_BOLD}{'='*50}{COLOR_RESET}")
    print(f"{COLOR_CYAN}{COLOR_BOLD}{title:^50}{COLOR_RESET}")
    print(f"{COLOR_CYAN}{COLOR_BOLD}{'='*50}{COLOR_RESET}\n")


def print_success(message: str):
    """打印成功信息"""
    print(f"{COLOR_GREEN}✓ {message}{COLOR_RESET}")


def print_error(message: str):
    """打印错误信息"""
    print(f"{COLOR_RED}✗ {message}{COLOR_RESET}")


def print_warning(message: str):
    """打印警告信息"""
    print(f"{COLOR_YELLOW}⚠ {message}{COLOR_RESET}")


def print_info(message: str):
    """打印信息"""
    print(f"{COLOR_BLUE}ℹ {message}{COLOR_RESET}")


# =============================================
# 文件操作函数
# =============================================

def ensure_data_directory():
    """确保数据目录存在"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)


def load_students_data() -> List[Dict[str, Any]]:
    """
    从JSON文件加载学生数据
    
    Returns:
        List[Dict[str, Any]]: 学生列表
    """
    ensure_data_directory()
    
    if not os.path.exists(STUDENTS_FILE):
        return []
    
    try:
        with open(STUDENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, Exception):
        return []


def save_students_data(students: List[Dict[str, Any]]) -> bool:
    """
    保存学生数据到JSON文件
    
    Args:
        students: 学生列表
    
    Returns:
        bool: 保存成功返回True
    """
    ensure_data_directory()
    
    try:
        with open(STUDENTS_FILE, "w", encoding="utf-8") as f:
            json.dump(students, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


def read_legacy_data() -> Optional[str]:
    """
    读取历史遗留数据文件（只读）
    
    Returns:
        Optional[str]: 文件内容，文件不存在返回None
    """
    from config import LEGACY_FILE
    
    if not os.path.exists(LEGACY_FILE):
        return None
    
    try:
        with open(LEGACY_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


def export_to_csv(students: List[Dict[str, Any]], 
                  filename: str, 
                  subjects: List[str]) -> bool:
    """
    导出学生数据到CSV文件
    
    Args:
        students: 学生列表
        filename: 文件名
        subjects: 科目列表
    
    Returns:
        bool: 导出成功返回True
    """
    if not students:
        return False
    
    ensure_data_directory()
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    try:
        with open(filepath, "w", newline="", encoding=CSV_ENCODING) as f:
            writer = csv.writer(f)
            # 表头
            headers = ["学号", "姓名", "性别", "年龄", "班级"] + subjects + ["总分", "平均分"]
            writer.writerow(headers)
            
            # 数据
            for student in students:
                row = [
                    student["id"],
                    student["name"],
                    student["gender"],
                    student["age"],
                    student["class"]
                ]
                for subject in subjects:
                    row.append(student["subjects"].get(subject, 0))
                row.append(student["total"])
                row.append(student["average"])
                writer.writerow(row)
        
        return True
    except Exception:
        return False


def import_from_csv(filepath: str, subjects: List[str]) -> List[Dict[str, Any]]:
    """
    从CSV文件导入学生数据
    
    Args:
        filepath: 文件路径
        subjects: 科目列表
    
    Returns:
        List[Dict[str, Any]]: 导入的学生列表
    """
    imported = []
    
    if not os.path.exists(filepath):
        return imported
    
    try:
        with open(filepath, "r", encoding=CSV_ENCODING) as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    # 读取科目成绩
                    subjects_scores = {}
                    for subject in subjects:
                        score_str = row.get(subject, "0")
                        try:
                            score = int(float(score_str))
                            score = max(0, min(100, score))
                        except ValueError:
                            score = 0
                        subjects_scores[subject] = score
                    
                    # 计算总分和平均分
                    total = sum(subjects_scores.values())
                    average = round(total / len(subjects_scores), 1) if subjects_scores else 0.0
                    
                    student = {
                        "id": row.get("学号", ""),
                        "name": row.get("姓名", ""),
                        "gender": row.get("性别", "男"),
                        "age": int(row.get("年龄", 18)),
                        "class": row.get("班级", ""),
                        "subjects": subjects_scores,
                        "total": total,
                        "average": average
                    }
                    
                    imported.append(student)
                    
                except Exception:
                    continue
        
        return imported
        
    except Exception:
        return []


def generate_markdown_report(students: List[Dict[str, Any]], 
                              subjects: List[str],
                              stats: Dict[str, Any]) -> bool:
    """
    生成Markdown格式成绩分析报告
    
    Args:
        students: 学生列表
        subjects: 科目列表
        stats: 统计信息字典
    
    Returns:
        bool: 生成成功返回True
    """
    from datetime import datetime
    
    ensure_data_directory()
    filepath = os.path.join(OUTPUT_DIR, "成绩分析报告.md")
    
    try:
        lines = []
        lines.append("# 成绩分析报告\n")
        lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # 总体统计
        lines.append("## 一、总体统计\n\n")
        lines.append(f"- **总人数**: {stats.get('total_count', 0)} 人\n")
        lines.append(f"- **班级平均总分**: {stats.get('class_average_total', 0)} 分\n")
        lines.append(f"- **班级平均平均分**: {stats.get('class_average_score', 0)} 分\n")
        lines.append(f"- **及格率**: {stats.get('passing_rate', 0)}%\n\n")
        
        # 前5名
        lines.append("## 二、总分排名（前5名）\n\n")
        lines.append("| 排名 | 学号 | 姓名 | 班级 | 总分 | 平均分 |\n")
        lines.append("|------|------|------|------|------|--------|\n")
        
        top5 = stats.get('top5', [])
        for i, student in enumerate(top5, 1):
            lines.append(f"| {i} | {student['id']} | {student['name']} | {student['class']} | {student['total']} | {student['average']} |\n")
        
        lines.append("\n")
        
        # 后3名
        lines.append("## 三、总分排名（后3名）\n\n")
        lines.append("| 排名 | 学号 | 姓名 | 班级 | 总分 | 平均分 |\n")
        lines.append("|------|------|------|------|------|--------|\n")
        
        bottom3 = stats.get('bottom3', [])
        total_count = len(students)
        for i, student in enumerate(bottom3, total_count - 2):
            lines.append(f"| {i} | {student['id']} | {student['name']} | {student['class']} | {student['total']} | {student['average']} |\n")
        
        lines.append("\n")
        
        # 各科目统计
        lines.append("## 四、各科目统计\n\n")
        lines.append("| 科目 | 平均分 | 最高分 | 最低分 |\n")
        lines.append("|------|--------|--------|--------|\n")
        
        subject_stats = stats.get('subject_stats', {})
        for subject in subjects:
            stat = subject_stats.get(subject, {})
            lines.append(f"| {subject} | {stat.get('average', 0)} | {stat.get('max', 0)} | {stat.get('min', 0)} |\n")
        
        lines.append("\n")
        
        # 不及格名单
        lines.append("## 五、不及格学生名单\n\n")
        failing = stats.get('failing_students', [])
        if failing:
            lines.append("| 学号 | 姓名 | 班级 | 平均分 |\n")
            lines.append("|------|------|------|--------|\n")
            for student in failing:
                lines.append(f"| {student['id']} | {student['name']} | {student['class']} | {student['average']} |\n")
        else:
            lines.append("无不及格学生\n")
        
        lines.append("\n---\n")
        lines.append("*本报告由学生成绩管理系统自动生成*\n")
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("".join(lines))
        
        return True
        
    except Exception:
        return False


# =============================================
# 表格打印函数
# =============================================

def print_table(headers: List[str], rows: List[List[Any]], 
                col_widths: Optional[List[int]] = None):
    """
    打印对齐的表格
    
    Args:
        headers: 表头列表
        rows: 数据行列表
        col_widths: 列宽列表（可选）
    """
    if not rows:
        print_info("暂无数据")
        return
    
    # 自动计算列宽
    if col_widths is None:
        col_widths = []
        for i, header in enumerate(headers):
            max_width = len(str(header))
            for row in rows:
                if i < len(row):
                    max_width = max(max_width, len(str(row[i])))
            col_widths.append(max_width + 2)
    
    # 打印分隔线
    separator = "+".join(["-" * w for w in col_widths])
    separator = "+" + separator + "+"
    
    # 打印表头
    print(separator)
    header_row = "|".join(str(h).ljust(w) for h, w in zip(headers, col_widths))
    print("|" + header_row + "|")
    print(separator)
    
    # 打印数据
    for row in rows:
        # 确保行数据与表头数量一致
        row_data = list(row) + [""] * (len(headers) - len(row))
        data_row = "|".join(str(d).ljust(w) for d, w in zip(row_data, col_widths))
        print("|" + data_row + "|")
    
    print(separator)


# =============================================
# 计算辅助函数
# =============================================

def calculate_total_and_average(subjects: Dict[str, int]) -> tuple:
    """
    计算总分和平均分
    
    Args:
        subjects: 科目成绩字典
    
    Returns:
        tuple: (总分, 平均分)
    """
    total = sum(subjects.values())
    average = round(total / len(subjects), 1) if subjects else 0.0
    return total, average


def calculate_rank(student_id: str, students: List[Dict[str, Any]]) -> int:
    """
    计算学生排名（处理并列）
    
    Args:
        student_id: 学号
        students: 学生列表
    
    Returns:
        int: 排名
    """
    # 按总分降序排序
    sorted_students = sorted(students, key=lambda x: x["total"], reverse=True)
    
    rank = 1
    prev_total = None
    
    for i, student in enumerate(sorted_students, 1):
        if prev_total is not None and student["total"] < prev_total:
            rank = i
        
        if student["id"] == student_id:
            return rank
        
        prev_total = student["total"]
    
    return 0


def generate_student_id(students: List[Dict[str, Any]], 
                        id_prefix: str, 
                        id_start: int) -> str:
    """
    自动生成学号
    
    Args:
        students: 学生列表
        id_prefix: 学号前缀
        id_start: 起始序号
    
    Returns:
        str: 自动生成的学号
    """
    existing_ids = {s["id"] for s in students}
    
    # 找出最大序号
    max_num = 0
    for sid in existing_ids:
        if sid.startswith(id_prefix):
            try:
                num = int(sid[len(id_prefix):])
                max_num = max(max_num, num)
            except ValueError:
                pass
    
    # 生成新学号
    new_num = max(max_num + 1, id_start)
    return f"{id_prefix}{new_num:04d}"
