# agentic-data-processor/src/conversion_tasks.py
import json
import csv
from .utils import setup_logging

logger = setup_logging(__name__)

class ConversionTasks:
    """
    Handles conversions between CSV (list of dicts) and JSON formats.
    """
    def __init__(self):
        logger.info("ConversionTasks initialized.")

    def csv_to_json(self, csv_data):
        """
        Converts CSV data (list of dictionaries) to JSON-compatible Python list of dicts.
        Numeric strings (including negative numbers) and booleans are converted to actual types.
        """
        if not csv_data:
            logger.warning("No CSV data to convert to JSON.")
            return []
        
        json_data = []
        for row in csv_data:
            json_row = {}
            for key, value in row.items():
                if not isinstance(value, str):
                    json_row[key] = value
                    continue

                val_str = value.strip()
                val_lower = val_str.lower()

                if val_lower in ['true', 'false']:
                    json_row[key] = (val_lower == 'true')
                elif val_lower in ['null', 'none', '']:
                    json_row[key] = None
                else:
                    # ลองแปลงเป็น Integer หรือ Float (รองรับตัวเลขติดลบ)
                    try:
                        if '.' in val_str:
                            json_row[key] = float(val_str)
                        else:
                            json_row[key] = int(val_str)
                    except ValueError:
                        json_row[key] = val_str

            json_data.append(json_row)
        
        logger.info(f"Converted {len(csv_data)} CSV rows to JSON format.")
        return json_data

    def json_to_csv(self, json_data, fieldnames=None):
        """
        Converts JSON data (list of dictionaries or single dict) to a CSV-compatible list of dictionaries.
        Flattens simple nested keys (e.g. details.brand).
        """
        if not json_data:
            logger.warning("No JSON data to convert to CSV.")
            return [], []

        # หากส่งมาเป็น dict ตัวเดียว ให้แปลงเป็น list
        if isinstance(json_data, dict):
            json_data = [json_data]

        csv_rows = []
        
        # ถ้าระบุ fieldnames มา หรือพยายามอ่าน fieldnames ทั้งหมด
        if fieldnames is None:
            all_keys = set()
            for item in json_data:
                if isinstance(item, dict):
                    for k, v in item.items():
                        if isinstance(v, dict):
                            for sub_k in v.keys():
                                all_keys.add(f"{k}.{sub_k}")
                        else:
                            all_keys.add(k)
            fieldnames = sorted(list(all_keys))
            logger.info(f"Inferred fieldnames for JSON to CSV: {fieldnames}")

        for item in json_data:
            if not isinstance(item, dict):
                csv_rows.append({"value": item})
                continue

            row = {}
            for field in fieldnames:
                if '.' in field:
                    parts = field.split('.')
                    current_val = item.get(parts[0])
                    if isinstance(current_val, dict):
                        row[field] = current_val.get(parts[1], '')
                    else:
                        row[field] = ''
                else:
                    value = item.get(field, '')
                    if isinstance(value, (dict, list)):
                        row[field] = json.dumps(value, ensure_ascii=False)
                    else:
                        row[field] = value
            csv_rows.append(row)
        
        logger.info(f"Converted {len(json_data)} JSON objects to CSV format.")
        return csv_rows, fieldnames