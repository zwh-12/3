#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心业务逻辑模块
职责：实现增删改查、统计分析、排名等业务算法
"""

from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict

from config import SUBJECTS, ID_PREFIX, ID_START, PAGE_SIZE, PASSING_SCORE
from utils import (
    calculate_total_and_average, calculate_rank, generate_student_id,
    load_students_data, save_students_data, export_to_csv, import_from_csv,
    generate_markdown_report, print_success, print_error, print_warning, print_info
)
from validator import (
    validate_student_id, validate_name, validate_gender, normalize_gender,
    validate_age, validate_score, validate_class_name, validate_student_data
)


class StudentProcessor:
    """
    学生处理器类
    封装所有学生数据操作的业务逻辑
    """
    
    def __init__(self):
        """初始化处理器"""
        self.students = load_students_data()
        self.subjects = SUBJECTS
    
    # =============================================
    # 基础CRUD操作
    # =============================================
    
    def add_student(self, student_id: str, name: str, gender: str, 
                    age: int, class_name: str, subjects_scores: Dict[str, int]) -> Tuple[bool, str]:
        """
        添加学生
        
        Args:
            student_id: 学号（如果为"自动"则自动生成）
            name: 姓名
            gender: 性别
            age: 年龄
            class_name: 班级
            subjects_scores: 科目成绩字典
        
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        # 处理自动生成学号
        if student_id == "自动":
            student_id = generate_student_id(self.students, ID_PREFIX, ID_START)
        
        # 验证学号
        is_valid, error = validate_student_id(student_id, self.students)
        if not is_valid:
            return False, error
        
        # 验证其他信息
        is_valid, error = validate_name(name)
        if not is_valid:
            return False, error
        
        is_valid, error = validate_gender(gender)
        if not is_valid:
            return False, error
        
        is_valid, error = validate_class_name(class_name)
        if not is_valid:
            return False, error
        
        # 标准化性别
        gender = normalize_gender(gender)
        
        # 计算总分和平均分
        total, average = calculate_total_and_average(subjects_scores)
        
        # 创建学生记录
        student = {
            "id": student_id,
            "name": name,
            "gender": gender,
            "age": age,
            "class": class_name,
            "subjects": subjects_scores,
            "total": total,
            "average": average
        }
        
        # 添加到列表
        self.students.append(student)
        
        # 保存数据
        if save_students_data(self.students):
            return True, f"学生 {name}（{student_id}）添加成功！总分：{total}，平均分：{average}"
        else:
            # 回滚
            self.students.pop()
            return False, "保存数据失败"
    
    def delete_student_by_id(self, student_id: str) -> Tuple[bool, str]:
        """
        按学号删除学生
        
        Args:
            student_id: 学号
        
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        student = self.find_by_id(student_id)
        
        if not student:
            return False, "未找到该学号的学生"
        
        self.students.remove(student)
        
        if save_students_data(self.students):
            return True, f"学生 {student['name']}（{student_id}）已删除"
        else:
            # 回滚
            self.students.append(student)
            return False, "保存数据失败"
    
    def delete_students_by_name(self, name: str) -> Tuple[List[Dict[str, Any]], str]:
        """
        按姓名删除学生（模糊匹配）
        
        Args:
            name: 姓名
        
        Returns:
            Tuple[List, str]: (匹配的学生列表, 消息)
        """
        matched = self.find_by_name(name)
        return matched, f"找到 {len(matched)} 个匹配结果"
    
    def update_student(self, student_id: str, 
                       updates: Dict[str, Any]) -> Tuple[bool, str]:
        """
        更新学生信息
        
        Args:
            student_id: 学号
            updates: 更新字段字典
        
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        student = self.find_by_id(student_id)
        
        if not student:
            return False, "未找到该学生"
        
        # 备份原数据
        old_data = student.copy()
        old_subjects = student["subjects"].copy()
        
        # 应用更新
        if "name" in updates:
            is_valid, error = validate_name(updates["name"])
            if not is_valid:
                return False, error
            student["name"] = updates["name"]
        
        if "gender" in updates:
            is_valid, error = validate_gender(updates["gender"])
            if not is_valid:
                return False, error
            student["gender"] = normalize_gender(updates["gender"])
        
        if "age" in updates:
            student["age"] = updates["age"]
        
        if "class" in updates:
            student["class"] = updates["class"]
        
        if "subjects" in updates:
            student["subjects"] = updates["subjects"]
            # 重新计算总分和平均分
            student["total"], student["average"] = calculate_total_and_average(student["subjects"])
        
        # 保存数据
        if save_students_data(self.students):
            return True, "更新成功"
        else:
            # 回滚
            student.update(old_data)
            student["subjects"] = old_subjects
            return False, "保存数据失败"
    
    def find_by_id(self, student_id: str) -> Optional[Dict[str, Any]]:
        """
        按学号查找学生
        
        Args:
            student_id: 学号
        
        Returns:
            Optional[Dict]: 学生字典或None
        """
        for student in self.students:
            if student["id"] == student_id:
                return student
        return None
    
    def find_by_name(self, name: str) -> List[Dict[str, Any]]:
        """
        按姓名模糊查找学生
        
        Args:
            name: 姓名
        
        Returns:
            List[Dict]: 学生列表
        """
        return [s for s in self.students if name in s["name"]]
    
    # =============================================
    # 查询与显示
    # =============================================
    
    def get_all_students_sorted(self) -> List[Dict[str, Any]]:
        """
        获取所有学生（按总分降序排序）
        
        Returns:
            List[Dict]: 排序后的学生列表
        """
        return sorted(self.students, key=lambda x: x["total"], reverse=True)
    
    def get_student_with_rank(self, student_id: str) -> Optional[Dict[str, Any]]:
        """
        获取学生信息（包含排名）
        
        Args:
            student_id: 学号
        
        Returns:
            Optional[Dict]: 包含排名的学生字典
        """
        student = self.find_by_id(student_id)
        
        if student:
            student = student.copy()
            student["rank"] = calculate_rank(student_id, self.students)
        
        return student
    
    def get_paginated_students(self, page: int = 1) -> Tuple[List[Dict[str, Any]], int, int]:
        """
        获取分页学生数据
        
        Args:
            page: 页码（从1开始）
        
        Returns:
            Tuple[List, int, int]: (当前页学生列表, 当前页码, 总页数)
        """
        sorted_students = self.get_all_students_sorted()
        total = len(sorted_students)
        total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
        
        # 确保页码有效
        page = max(1, min(page, total_pages)) if total_pages > 0 else 1
        
        start_idx = (page - 1) * PAGE_SIZE
        end_idx = min(start_idx + PAGE_SIZE, total)
        
        # 添加排名信息
        page_students = []
        for i, student in enumerate(sorted_students[start_idx:end_idx], start_idx + 1):
            student_with_rank = student.copy()
            
            # 计算排名（处理并列）
            rank = i
            if i > 1 and student["total"] == sorted_students[start_idx + i - start_idx - 2]["total"]:
                rank = page_students[-1]["rank"]
            
            student_with_rank["rank"] = rank
            page_students.append(student_with_rank)
        
        return page_students, page, total_pages
    
    # =============================================
    # 统计与分析
    # =============================================
    
    def calculate_statistics(self) -> Dict[str, Any]:
        """
        计算成绩统计信息
        
        Returns:
            Dict[str, Any]: 统计信息字典
        """
        if not self.students:
            return {}
        
        sorted_students = self.get_all_students_sorted()
        total_count = len(self.students)
        
        # 前5名和后3名
        top5 = sorted_students[:5]
        bottom3 = sorted_students[-3:] if total_count >= 3 else sorted_students
        
        # 各科目统计
        subject_stats = {}
        for subject in self.subjects:
            scores = [s["subjects"][subject] for s in self.students]
            subject_stats[subject] = {
                "average": round(sum(scores) / len(scores), 1),
                "max": max(scores),
                "min": min(scores)
            }
        
        # 班级整体统计
        all_totals = [s["total"] for s in self.students]
        all_averages = [s["average"] for s in self.students]
        
        # 及格率
        passing_count = sum(1 for s in self.students if s["average"] >= PASSING_SCORE)
        passing_rate = round(passing_count / total_count * 100, 1)
        
        # 不及格学生
        failing_students = [s for s in self.students if s["average"] < PASSING_SCORE]
        
        return {
            "total_count": total_count,
            "class_average_total": round(sum(all_totals) / total_count, 1),
            "class_average_score": round(sum(all_averages) / total_count, 1),
            "passing_rate": passing_rate,
            "top5": top5,
            "bottom3": bottom3,
            "subject_stats": subject_stats,
            "failing_students": failing_students
        }
    
    def filter_students(self, filter_type: str, **kwargs) -> List[Dict[str, Any]]:
        """
        筛选学生
        
        Args:
            filter_type: 筛选类型
            **kwargs: 额外参数
        
        Returns:
            List[Dict]: 筛选后的学生列表
        """
        if filter_type == "average_above":
            threshold = kwargs.get("threshold", 60)
            return [s for s in self.students if s["average"] >= threshold]
        
        elif filter_type == "subject_failing":
            subject = kwargs.get("subject", "")
            if subject in self.subjects:
                return [s for s in self.students if s["subjects"][subject] < PASSING_SCORE]
            return []
        
        elif filter_type == "class":
            class_name = kwargs.get("class_name", "")
            return [s for s in self.students if class_name in s["class"]]
        
        return []
    
    def generate_report(self) -> Tuple[bool, str]:
        """
        生成成绩分析报告
        
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        stats = self.calculate_statistics()
        
        if not stats:
            return False, "没有数据可生成报告"
        
        if generate_markdown_report(self.students, self.subjects, stats):
            return True, "成绩分析报告已生成"
        else:
            return False, "生成报告失败"
    
    # =============================================
    # 导入导出
    # =============================================
    
    def export_students(self, filename: str) -> Tuple[bool, str]:
        """
        导出学生数据
        
        Args:
            filename: 文件名
        
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        if not self.students:
            return False, "没有数据可导出"
        
        if export_to_csv(self.students, filename, self.subjects):
            return True, f"数据已导出到 {filename}"
        else:
            return False, "导出失败"
    
    def import_students(self, filename: str) -> Tuple[int, str]:
        """
        导入学生数据
        
        Args:
            filename: 文件名
        
        Returns:
            Tuple[int, str]: (导入数量, 消息)
        """
        import os
        from config import INPUT_DIR
        
        filepath = os.path.join(INPUT_DIR, filename) if not os.path.exists(filename) else filename
        
        imported = import_from_csv(filepath, self.subjects)
        
        # 过滤已存在的学号
        new_students = []
        for student in imported:
            if not self.find_by_id(student["id"]):
                new_students.append(student)
        
        self.students.extend(new_students)
        save_students_data(self.students)
        
        return len(new_students), f"成功导入 {len(new_students)} 条记录（跳过 {len(imported) - len(new_students)} 条重复）"
    
    def import_from_legacy(self) -> Tuple[int, str]:
        """
        从legacy.dat导入数据（初始化用）
        
        Returns:
            Tuple[int, str]: (导入数量, 消息)
        """
        from utils import read_legacy_data
        import io
        import csv
        
        content = read_legacy_data()
        
        if not content:
            return 0, "legacy.dat 文件不存在或为空"
        
        # 解析legacy数据（CSV格式）
        imported = []
        try:
            f = io.StringIO(content)
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    subjects_scores = {}
                    for subject in self.subjects:
                        score_str = row.get(subject, "0")
                        try:
                            score = int(float(score_str))
                        except ValueError:
                            score = 0
                        subjects_scores[subject] = score
                    
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
        except Exception:
            pass
        
        # 过滤已存在的学号
        new_students = []
        for student in imported:
            if not self.find_by_id(student["id"]):
                new_students.append(student)
        
        self.students.extend(new_students)
        save_students_data(self.students)
        
        return len(new_students), f"从 legacy.dat 导入 {len(new_students)} 条记录"
