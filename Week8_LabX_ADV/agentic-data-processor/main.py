# agentic-data-processor/main.py
import sys
import os

from src.config_parser import ConfigParser
from src.pipeline_runner import PipelineRunner
from src.utils import setup_logging, ensure_directory_exists

logger = setup_logging(__name__)

def check_required_input_files(config):
    """
    ตรวจสอบว่าไฟล์ Input ทั้งหมดที่ต้องใช้ใน Config มีอยู่จริงก่อนเริ่มรัน
    """
    required_files_exist = True
    for task in config.get('tasks', []):
        if task.get('type') in ['load_csv', 'load_json']:
            file_path = task.get('file_path')
            if file_path and not os.path.exists(file_path):
                logger.critical(f"ไม่พบไฟล์ Input: '{file_path}' สำหรับ Task '{task.get('type')}'")
                required_files_exist = False
    return required_files_exist

def main():
    """
    Main entry point สำหรับรัน Data Pipeline
    """
    base_dir = os.path.dirname(__file__)
    config_file_path = os.path.join(base_dir, 'configs', 'data_pipeline_config.json')
    
    # หากไม่พบไฟล์ใน configs/ ให้ลองค้นหา config.json ใน root directory
    if not os.path.exists(config_file_path):
        config_file_path = os.path.join(base_dir, 'config.json')

    try:
        # สร้างโฟลเดอร์ที่จำเป็นให้อัตโนมัติหากยังไม่มี
        ensure_directory_exists(os.path.join(base_dir, 'data'))
        ensure_directory_exists(os.path.join(base_dir, 'configs'))
        ensure_directory_exists(os.path.join(base_dir, 'reports'))

        logger.info(f"กำลังโหลด Config จาก: {config_file_path}")
        config_parser = ConfigParser(config_file_path)
        config = config_parser.load_config()

        # ตรวจสอบไฟล์ Input ก่อนเริ่มรัน
        if not check_required_input_files(config):
            logger.critical("ไม่สามารถเริ่มการทำงานได้ เนื่องจากขาดไฟล์ Input ที่จำเป็น")
            return

        logger.info("เริ่มต้นสั่งงาน PipelineRunner...")
        runner = PipelineRunner(config_file_path)
        runner.run()

        logger.info("กระบวนการประมวลผลข้อมูลเสร็จสมบูรณ์เรียบร้อยแล้ว")

    except FileNotFoundError as e:
        logger.critical(f"เกิดข้อผิดพลาดกับระบบไฟล์: {e}")
    except ValueError as e:
        logger.critical(f"เกิดข้อผิดพลาดใน Config: {e}")
    except Exception as e:
        logger.critical(f"เกิดข้อผิดพลาดที่ไม่คาดคิดระหว่างการทำงาน: {e}", exc_info=True)

if __name__ == "__main__":
    main()