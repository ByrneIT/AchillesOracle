from scanner.engine import ScannerEngine
from scanner.report import ReportBuilder

engine = ScannerEngine("https://example.com")
results = engine.run()

report = ReportBuilder("https://example.com", results)

print("Summary:", report.summary())
print("\nFull JSON report:\n")
print(report.to_json())


#for r in results:
#	print(r)
