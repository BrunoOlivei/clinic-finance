import argparse
import sys
from datetime import date, datetime

from src.core.logger import logger
from src.savi.production_reports.pipeline import ProductionReportPipeline

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--month-competency", default=date.today().strftime("%m/%Y"))
    args = parser.parse_args()

    try:
        datetime.strptime(args.month_competency, "%m/%Y")
    except ValueError:
        logger.error("Formato de data inválido: {}", args.month_competency)
        sys.exit(1)

    ProductionReportPipeline(args.month_competency).main()
