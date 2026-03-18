#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
输入验证与数据校验模块
职责：提供所有输入验证和数据校验功能
"""

from typing import List, Dict, Any, Tuple

from config import SCORE_MIN, SCORE_MAX, AGE_MIN, AGE_MAX


# =============================================
# 输入验证函数
# =============================================

def validate_student_id(student_id: str, existing_students: List[Dict[str, Any]]) -> Tuple[bool, str]:
    """
    验证学号
    
    Args:
        student_id: 学号
        existing_students: 现有学生列表
    
    Returns:
        Tuple[bool, str]: (是否有效, 错误信息)
    """
    if not student_id:
        return False, "学号不能为空"
    
    if len(student_id) < 3:
        return False, "学号长度至少为3位"
    
    # 检查学号是否已存在
    for student in existing_students:
        if student["id"] == student_id:
            return False, f"学号 {student_id} 已存在"
    
    return True, ""


def validate_name(name: str) -> Tuple[bool, str]:
    """
    验证姓名
    
    Args:
        name: 姓名
    
    Returns:
        Tuple[bool, str]: (是否有效, 错误信息)
    """
    if not name or not name.strip():
        return False, "姓名不能为空"
    
    if len(name) > 50:
        return False, "姓名过长（最多50个字符）"
    
    return True, ""


def validate_gender(gender: str) -> Tuple[bool, str]:
    """
    验证性别
    
    Args:
        gender: 性别
    
    Returns:
        Tuple[bool, str]: (是否有效, 错误信息)
    """
    valid_genders = ["男", "女", "M", "F", "m", "f"]
    if gender not in valid_genders:
        return False, "性别必须是 男/M 或 女/F"
    
    return True, ""


def normalize_gender(gender: str) -> str:
    """
    标准化性别
    
    Args:
        gender: 原始性别输入
    
    Returns:
        str: 标准化后的性别（男/女）
    """
    if gender in ["M", "m", "男"]:
        return "男"
    return "女"


def validate_age(age_str: str) -> Tuple[bool, int, str]:
    """
    验证年龄
    
    Args:
        age_str: 年龄字符串
    
    Returns:
        Tuple[bool, int, str]: (是否有效, 年龄值, 错误信息)
    """
    try:
        age = int(age_str)
    except ValueError:
        return False, 0, "年龄必须是整数"
    
    if age < AGE_MIN or age > AGE_MAX:
        return False, age, f"年龄必须在 {AGE_MIN}-{AGE_MAX} 岁之间"
    
    return True, age, ""


def validate_score(score_str: str) -> Tuple[bool, int, str]:
    """
    验证成绩
    
    Args:
        score_str: 成绩字符串
    
    Returns:
        Tuple[bool, int, str]: (是否有效, 成绩值, 错误信息)
    """
    try:
        score = int(float(score_str))
    except ValueError:
        return False, 0, "成绩必须是数值"
    
    if score < SCORE_MIN or score > SCORE_MAX:
        return False, score, f"成绩必须在 {SCORE_MIN}-{SCORE_MAX} 分之间"
    
    return True, score, ""


def validate_class_name(class_name: str) -> Tuple[bool, str]:
    """
    验证班级名称
    
    Args:
        class_name: 班级名称
    
    Returns:
        Tuple[bool, str]: (是否有效, 错误信息)
    """
    if not class_name or not class_name.strip():
        return False, "班级名称不能为空"
    
    return True, ""


def validate_choice(choice: str, valid_choices: List[str]) -> Tuple[bool, str]:
    """
    验证菜单选择
    
    Args:
        choice: 用户选择
        valid_choices: 有效选项列表
    
    Returns:
        Tuple[bool, str]: (是否有效, 错误信息)
    """
    if choice not in valid_choices:
        return False, f"无效选择，请输入：{'/'.join(valid_choices)}"
    
    return True, ""


def validate_file_exists(filepath: str) -> Tuple[bool, str]:
    """
    验证文件是否存在
    
    Args:
        filepath: 文件路径
    
    Returns:
        Tuple[bool, str]: (是否存在, 错误信息)
    """
    import os
    
    if not os.path.exists(filepath):
        return False, f"文件 {filepath} 不存在"
    
    return True, ""


# =============================================
# 数据校验函数
# =============================================

def validate_student_data(student: Dict[str, Any], 
                          existing_students: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
    """
    验证完整学生数据
    
    Args:
        student: 学生字典
        existing_students: 现有学生列表
    
    Returns:
        Tuple[bool, List[str]]: (是否有效, 错误信息列表)
    """
    errors = []
    
    # 验证学号
    is_valid, error = validate_student_id(student.get("id", ""), existing_students)
    if not is_valid:
        errors.append(error)
    
    # 验证姓名
    is_valid, error = validate_name(student.get("name", ""))
    if not is_valid:
        errors.append(error)
    
    # 验证性别
    is_valid, error = validate_gender(student.get("gender", ""))
    if not is_valid:
        errors.append(error)
    
    # 验证年龄
    age = student.get("age", 0)
    if not isinstance(age, int) or age < AGE_MIN or age > AGE_MAX:
        errors.append(f"年龄必须在 {AGE_MIN}-{AGE_MAX} 岁之间")
    
    # 验证班级
    is_valid, error = validate_class_name(student.get("class", ""))
    if not is_valid:
        errors.append(error)
    
    # 验证科目成绩
    subjects = student.get("subjects", {})
    for subject, score in subjects.items():
        is_valid, _, error = validate_score(str(score))
        if not is_valid:
            errors.append(f"{subject}：{error}")
    
    return len(errors) == 0, errors
