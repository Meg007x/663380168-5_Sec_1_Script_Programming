import json
import os
from .utils import setup_logging

logger = setup_logging(__name__)

class ConfigParser:
    """
    Parses and validates the data automation configuration from a JSON file.
    """
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = {}

    def load_config(self):
        """Loads the configuration from the specified JSON file."""
        if not os.path.exists(self.config_path):
            logger.critical(f"Configuration file not found: {self.config_path}")
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            self._validate_config()
            logger.info(f"Configuration loaded successfully from {self.config_path}")
            return self.config
        except (json.JSONDecodeError, ValueError, FileNotFoundError) as e:
            logger.critical(f"Validation or JSON parsing error: {e}")
            raise
        except Exception as e:
            logger.critical(f"An error occurred while loading config: {e}")
            raise Exception(f"An error occurred while loading config: {e}")

    def _validate_config(self):
        """
        Validates the loaded configuration to ensure required fields and task structures are present.
        """
        if "tasks" not in self.config:
            raise ValueError("Missing required field in config: 'tasks'")
        
        if not isinstance(self.config["tasks"], list):
            raise ValueError("Config field 'tasks' must be a list.")
        
        for i, task in enumerate(self.config["tasks"]):
            if "type" not in task:
                raise ValueError(f"Task {i} is missing 'type' field.")
            
            # Task ที่ไม่ได้เซฟลงไฟล์ ต้องระบุ output_data_key เพื่อเก็บข้อมูลใน Memory
            if task["type"] not in ["save_csv", "save_json"] and "output_data_key" not in task:
                raise ValueError(f"Task {i} (type: {task['type']}) is missing 'output_data_key' field.")

            # Task เกี่ยวกับไฟล์ ต้องระบุ file_path
            if task["type"] in ["load_csv", "load_json", "save_csv", "save_json"]:
                if "file_path" not in task:
                    raise ValueError(f"Task {i} (type: {task['type']}) requires 'file_path'.")
            
            # Task ที่ต้องดึงข้อมูลเดิมมาประมวลผล ต้องระบุ input_data_key
            if task["type"] in [
                "save_csv", "save_json",
                "transform_csv_aggregate", "filter_csv",
                "csv_to_json_conversion", "json_to_csv_conversion",
                "update_json", "query_json"
            ]:
                if "input_data_key" not in task:
                    raise ValueError(f"Task {i} (type: {task['type']}) requires 'input_data_key'.")

            if task["type"] == "save_csv":
                if "fieldnames" not in task and "input_data_key" not in task:
                    logger.warning(f"Task {i} (save_csv) has no explicit 'fieldnames'. Will attempt to derive from data.")

        logger.info("Configuration validated.")