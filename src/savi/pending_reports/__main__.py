import argparse
import sys
from calendar import monthrange
from datetime import datetime, timedelta

from src.core.logger import logger
from src.savi.pending_reports.pipeline import PendingReportPipeline

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--month-competency", default="09/2025")
    args = parser.parse_args()

    try:
        start_date = datetime.strptime(args.month_competency, "%m/%Y")
    except ValueError:
        logger.error("Formato de data inválido: {}", args.month_competency)
        sys.exit(1)

    while start_date <= datetime(datetime.now().year, datetime.now().month, 1):
        logger.info("Processando {}", start_date.strftime("%m/%Y"))
        PendingReportPipeline(start_date.strftime("%m/%Y")).main()
        month_days = monthrange(start_date.year, start_date.month)[1]
        start_date += timedelta(days=month_days)
