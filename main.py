from src.savi.pending_reports.pipeline import PendingReportPipeline
from src.savi.production_reports.pipeline import ProductionReportPipeline

MONTH_COMPETENCY = "07/2026"

ProductionReportPipeline(MONTH_COMPETENCY).main()
PendingReportPipeline(MONTH_COMPETENCY).main()
