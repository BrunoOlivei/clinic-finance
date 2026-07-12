# from src.production_reports.extract_data import ProductionReportExtractor
# from src.production_reports.parser_data import ProductionReportParser
from src.pending_reports.extract_data import PendingReportExtractor

with PendingReportExtractor() as report:
    report.login()
    html = report.fetch("06/2026")

print(html)
# teste = ProductionReportParser(html).parse()
# for item in teste:
#     print(item)
