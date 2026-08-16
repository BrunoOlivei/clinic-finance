# import sys
# from datetime import datetime

# from src.core.logger import logger
# from src.savi.pending_reports.pipeline import PendingReportPipeline
# from src.savi.production_reports.pipeline import ProductionReportPipeline

# MONTH_COMPETENCY = "08/2026"

# if __name__ == "__main__":
#     try:
#         datetime.strptime(MONTH_COMPETENCY, "%m/%Y")
#     except ValueError:
#         logger.error("Formato de data inválido: {}", MONTH_COMPETENCY)
#         sys.exit(1)

#     ProductionReportPipeline(MONTH_COMPETENCY).main()
#     PendingReportPipeline(MONTH_COMPETENCY).main()


from src.core.db import run_query

print(run_query("SELECT * FROM mart_faturamento LIMIT 5"))