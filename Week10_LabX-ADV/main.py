# main.py
import sys
import os
from src.utils import setup_logging

logger = setup_logging(__name__)
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config_parser import ConfigParser
from spreadsheet_agent import SpreadsheetAgent

def main():
    config_file_path = os.path.join(os.path.dirname(__file__), 'configs', 'example_spreadsheet_config.json')
    try:
        os.makedirs('data', exist_ok=True)
        logger.info(f"Loading configuration from: {config_file_path}")
        config_parser = ConfigParser(config_file_path)
        config = config_parser.load_config()
        
        input_file_path = config.get("input_file")
        if not os.path.exists(input_file_path):
            logger.critical(f"❌ Input file not found: '{input_file_path}'")
            return
        
        logger.info("Initializing Spreadsheet Agent...")
        agent = SpreadsheetAgent(config)
        logger.info("Running Spreadsheet Agent...")
        agent.run()
    except Exception as e:
        logger.critical(f"Critical error: {e}", exc_info=True)

if __name__ == "__main__":
    main()
