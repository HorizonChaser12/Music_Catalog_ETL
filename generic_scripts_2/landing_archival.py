from datetime import datetime
import logging
import sys
from generic_scripts_2.utils.postgres_connection import get_connection
from pathlib import Path

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def clear_raw_files(source_name):
    """Remove older raw files and keep the latest 5 matching files."""
    raw_dir = Path(f"/opt/project/data/raw/{source_name}")
    logger.info(f"Checking for redundant raw_data in {raw_dir}")

    if not raw_dir.exists():
        raise FileNotFoundError(f"Raw directory does not exist: {raw_dir}")

    files = sorted(raw_dir.glob(f"{source_name}_*.json"))
    if not files:
        raise FileNotFoundError(f"No {source_name} files found in {raw_dir}")

    if len(files) <= 2:
        logger.info(f"Found {len(files)} file(s); nothing to remove.")
        return

    stale_files = files[:-2]
    for stale_file in stale_files:
        stale_file.unlink()
        logger.info(f"Removed file {stale_file} from {raw_dir}")
    


def main():
    """Main entry point for clearing raw_data."""
    # Validate arguments
    if len(sys.argv) !=2:
        print("Usage: python landing_archival.py <source_name>")
        sys.exit(1)
    source_names = sys.argv[1].split(",")  
    
    try:
        for source_name in source_names:
            clear_raw_files(source_name)
    except Exception as E:
        logger.error(f"Failed to clean files: {E}")

        
if __name__ == "__main__":
    main()
