import schedule
import time
import subprocess
import logging
import os
from datetime import datetime
import sys

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log', mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)


def get_script_path(script_name):
    """Get the absolute path to a script"""
    # Get the directory where this orchestrator script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # If we're already in the scripts directory, go up one level to project root
    if os.path.basename(script_dir) == 'scripts':
        project_root = os.path.dirname(script_dir)
        return os.path.join(project_root, 'scripts', script_name)
    else:
        # We're in project root already
        return os.path.join('scripts', script_name)


def run_script(script_name):
    """Run a Python script and return success status"""
    logging.info(f"Running {script_name}...")
    try:
        script_path = get_script_path(script_name)
        logging.info(f"Script path: {script_path}")
        python_executable = sys.executable
        result = subprocess.run(
            [python_executable, script_path],
            capture_output=True,
            text=True,
            check=True,
            timeout=300
        )
        if result.stdout:
            logging.info(f"{script_name} output: {result.stdout.strip()}")
        logging.info(f"{script_name} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"{script_name} failed with error: {e.stderr}")
        return False
    except subprocess.TimeoutExpired:
        logging.error(f"{script_name} timed out after 5 minutes")
        return False
    except Exception as e:
        logging.error(f"{script_name} failed with unexpected error: {e}")
        return False


def run_pipeline():
    """Run the complete news pipeline"""
    logging.info("=" * 60)
    logging.info("STARTING COMPLETE NEWS PIPELINE RUN")
    logging.info("=" * 60)

    start_time = datetime.now()

    # Run ingestion
    success1 = run_script('ingestion.py')

    # Only run processing if ingestion succeeded
    if success1:
        success2 = run_script('processing.py')
    else:
        logging.error("Skipping processing due to ingestion failure")
        success2 = False

    end_time = datetime.now()
    duration = end_time - start_time

    logging.info("=" * 60)
    if success1 and success2:
        logging.info(f"PIPELINE SUCCESS! Completed in {duration}")
    else:
        logging.error(f"PIPELINE FAILED after {duration}")
    logging.info("=" * 60)

    return success1 and success2


if __name__ == "__main__":
    logging.info("Starting News Pipeline Scheduler")
    logging.info("Will run every 4 hours automatically")

    # Run immediately on startup
    run_pipeline()

    # Schedule to run every 4 hours
    schedule.every(4).hours.do(run_pipeline)

    logging.info("Scheduler started successfully!")
    logging.info("Next run: Every 4 hours automatically")
    logging.info("Check pipeline.log for detailed logs")
    logging.info("Press Ctrl+C to stop the scheduler")

    # Keep the scheduler running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        logging.info("Scheduler stopped by user")
