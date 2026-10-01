# agentic-data-processor/src/pipeline_runner.py
from .config_parser import ConfigParser
from .csv_tasks import CSVTasks
from .json_tasks import JSONTasks
from .conversion_tasks import ConversionTasks
from .utils import setup_logging

logger = setup_logging(__name__)

class PipelineRunner:
    """
    คลาสควบคุมการทำงานของ Pipeline รับหน้าที่อ่าน Config และรัน Task ตามลำดับ
    """
    def __init__(self, config_path: str):
        self.config_parser = ConfigParser(config_path)
        self.config = {}
        self.data_store = {}  # หน่วยความจำชั่วคราวเก็บผลลัพธ์ของแต่ละ Task
        
        self.csv_handler = CSVTasks()
        self.json_handler = JSONTasks()
        self.conversion_handler = ConversionTasks()

    def run(self):
        """เริ่มต้นรัน Pipeline ตามรายการ tasks ใน Config"""
        logger.info("--- เริ่มต้นการทำงานของ Pipeline ---")
        self.config = self.config_parser.load_config()
        
        tasks = self.config.get("tasks", [])
        for index, task in enumerate(tasks, start=1):
            task_type = task.get("type")
            logger.info(f"กำลังดำเนินการ Task {index}/{len(tasks)}: [{task_type}]")
            self._execute_task(task)

        logger.info("--- การทำงานของ Pipeline เสร็จสมบูรณ์ทุกขั้นตอน ---")
        return self.data_store

    def _execute_task(self, task: dict):
        task_type = task.get("type")
        input_key = task.get("input_data_key")
        output_key = task.get("output_data_key")
        file_path = task.get("file_path")

        # 1. โหลดข้อมูล CSV
        if task_type == "load_csv":
            read_fn = getattr(self.csv_handler, "read_csv_task", None) or getattr(self.csv_handler, "read_csv", None)
            self.data_store[output_key] = read_fn(file_path)

        # 2. โหลดข้อมูล JSON
        elif task_type == "load_json":
            load_fn = getattr(self.json_handler, "load_json", None) or getattr(self.json_handler, "read_json_task", None)
            self.data_store[output_key] = load_fn(file_path)

        # 3. บันทึกข้อมูลเป็น CSV
        elif task_type == "save_csv":
            data = self.data_store.get(input_key)
            fieldnames = task.get("fieldnames")
            write_fn = getattr(self.csv_handler, "write_csv_task", None) or getattr(self.csv_handler, "write_csv", None)
            write_fn(data, file_path, fieldnames=fieldnames)

        # 4. บันทึกข้อมูลเป็น JSON
        elif task_type == "save_json":
            data = self.data_store.get(input_key)
            indent = task.get("indent", 2)
            save_fn = getattr(self.json_handler, "save_json", None) or getattr(self.json_handler, "write_json_task", None)
            save_fn(data, file_path, indent=indent)

        # 5. สรุปผลข้อมูล CSV (Group By / Aggregate)
        elif task_type == "transform_csv_aggregate":
            data = self.data_store.get(input_key, [])
            group_by = task.get("group_by") or task.get("group_by_key")
            agg_key = task.get("aggregate_key")
            op = task.get("operation", "sum")
            self.data_store[output_key] = self.csv_handler.transform_csv_aggregate(
                data=data, group_by_key=group_by, aggregate_key=agg_key, operation=op
            )

        # 6. กรองข้อมูล CSV (Filter)
        elif task_type == "filter_csv":
            data = self.data_store.get(input_key, [])
            filter_key = task.get("filter_key")
            operator = task.get("operator")
            value = task.get("value")
            self.data_store[output_key] = self.csv_handler.filter_csv(
                data=data, filter_key=filter_key, operator=operator, value=value
            )

        # 7. แปลงข้อมูล CSV เป็น JSON
        elif task_type == "csv_to_json_conversion":
            data = self.data_store.get(input_key, [])
            conv_fn = getattr(self.conversion_handler, "csv_to_json", None) or getattr(self.conversion_handler, "csv_to_json_data", None)
            self.data_store[output_key] = conv_fn(data)

        # 8. แปลงข้อมูล JSON เป็น CSV
        elif task_type == "json_to_csv_conversion":
            data = self.data_store.get(input_key, [])
            conv_fn = getattr(self.conversion_handler, "json_to_csv", None) or getattr(self.conversion_handler, "json_to_csv_data", None)
            result = conv_fn(data)
            # รองรับกรณีคืนค่าแบบ tuple (rows, fieldnames) หรือ list
            if isinstance(result, tuple):
                self.data_store[output_key] = result[0]
            else:
                self.data_store[output_key] = result

        # 9. อัปเดตข้อมูล JSON
        elif task_type == "update_json":
            data = self.data_store.get(input_key)
            updates = task.get("updates", [])
            # หาก updates ส่งมาเป็น dict เดี่ยว ให้แปลงเป็น list
            if isinstance(updates, dict):
                updates = [updates]
            
            # รองรับทั้งแบบส่ง list updates หรือ path/value ตรงๆ
            if not updates and "path" in task:
                updates = [{"path": task.get("path"), "value": task.get("value"), "operation": task.get("operation", "set")}]

            self.data_store[output_key] = self.json_handler.update_json_data(data, updates)

        # 10. ค้นหาข้อมูล JSON (Query)
        elif task_type == "query_json":
            data = self.data_store.get(input_key)
            path = task.get("path")
            self.data_store[output_key] = self.json_handler.query_json_data(data, path)

        else:
            raise ValueError(f"ไม่พบ Task ประเภท: {task_type}")