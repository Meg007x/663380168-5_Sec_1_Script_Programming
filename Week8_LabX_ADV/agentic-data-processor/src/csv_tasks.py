import csv
import os
from typing import List, Dict, Any, Optional
from .utils import setup_logging, ensure_directory_exists

logger = setup_logging(__name__)

class CSVTasks:
    """
    คลาสสำหรับจัดการ Task เกี่ยวกับข้อมูล CSV ทั้งหมดใน Pipeline
    """

    @staticmethod
    def read_csv_task(file_path: str) -> List[Dict[str, Any]]:
        """อ่านไฟล์ CSV และแปลงข้อมูลแต่ละแถวเป็น Dictionary"""
        if not os.path.exists(file_path):
            logger.error(f"ไม่พบไฟล์ CSV ที่ตำแหน่ง: {file_path}")
            raise FileNotFoundError(f"ไม่พบไฟล์: {file_path}")
        
        data = []
        try:
            with open(file_path, mode='r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(dict(row))
            logger.info(f"อ่านข้อมูลจาก {file_path}สำเร็จ (จำนวน {len(data)} รายการ)")
            return data
        except Exception as e:
            logger.error(f"เกิดข้อผิดพลาดในการอ่านไฟล์ {file_path}: {e}")
            raise

    @staticmethod
    def write_csv_task(data: List[Dict[str, Any]], file_path: str, fieldnames: Optional[List[str]] = None) -> bool:
        """เขียนข้อมูล List of Dicts ลงไฟล์ CSV"""
        if not data and not fieldnames:
            logger.warning(f"ไม่มีข้อมูลและไม่ได้ระบุ fieldnames สำหรับไฟล์ {file_path}")
            return False

        ensure_directory_exists(os.path.dirname(file_path))

        if not fieldnames and data:
            fieldnames = list(data[0].keys())

        try:
            with open(file_path, mode='w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                if data:
                    writer.writerows(data)
            logger.info(f"บันทึกไฟล์ CSV สำเร็จ: {file_path}")
            return True
        except Exception as e:
            logger.error(f"เกิดข้อผิดพลาดในการบันทึกไฟล์ {file_path}: {e}")
            raise

    @staticmethod
    def transform_csv_aggregate(
        data: List[Dict[str, Any]], 
        group_by_key: str, 
        aggregate_key: str, 
        operation: str = "sum"
    ) -> List[Dict[str, Any]]:
        """จัดกลุ่มข้อมูล (Group By) แล้วคำนวณผลรวม (SUM) หรือค่าเฉลี่ย (AVG)"""
        if not data:
            return []

        grouped = {}
        counts = {}

        for row in data:
            group_val = row.get(group_by_key)
            try:
                agg_val = float(row.get(aggregate_key, 0))
            except (ValueError, TypeError):
                agg_val = 0.0

            if group_val not in grouped:
                grouped[group_val] = 0.0
                counts[group_val] = 0

            grouped[group_val] += agg_val
            counts[group_val] += 1

        result = []
        for group_val, total in grouped.items():
            if operation.lower() == "sum":
                final_val = total
            elif operation.lower() in ["avg", "average"]:
                final_val = total / counts[group_val] if counts[group_val] > 0 else 0.0
            else:
                raise ValueError(f"ไม่รองรับ Operation: {operation}")

            result.append({
                group_by_key: group_val,
                f"{aggregate_key}_{operation.lower()}": round(final_val, 2)
            })

        logger.info(f"ทำการ Aggregate ข้อมูลตาม '{group_by_key}' สำเร็จ (จำนวน {len(result)} กลุ่ม)")
        return result

    @staticmethod
    def filter_csv(
        data: List[Dict[str, Any]], 
        filter_key: str, 
        operator: str, 
        value: Any
    ) -> List[Dict[str, Any]]:
        """กรองข้อมูลตามเงื่อนไข (เช่น >, <, ==, !=, in)"""
        filtered = []
        for row in data:
            row_val = row.get(filter_key)
            
            # พยายามแปลงชนิดข้อมูลให้เปรียบเทียบได้
            try:
                if isinstance(value, (int, float)):
                    row_val = float(row_val)
            except (ValueError, TypeError):
                pass

            match = False
            if operator == "==":
                match = row_val == value
            elif operator == "!=":
                match = row_val != value
            elif operator == ">":
                match = row_val > value
            elif operator == ">=":
                match = row_val >= value
            elif operator == "<":
                match = row_val < value
            elif operator == "<=":
                match = row_val <= value
            elif operator == "in":
                match = row_val in value
            else:
                raise ValueError(f"ไม่รองรับ Operator: {operator}")

            if match:
                filtered.append(row)

        logger.info(f"กรองข้อมูลสำเร็จ: เงื่อนไข '{filter_key} {operator} {value}' เหลือ {len(filtered)} รายการ")
        return filtered