import importlib
import pkgutil
from scanner.checks import __path__ as checks_path
from scanner.checks.security_score_check import run_check as score_check

class ScannerEngine:
    def __init__(self, target_url):
        self.target_url = target_url
        self.checks = self._load_checks()

    def _load_checks(self):
        checks = []
        for module_info in pkgutil.iter_modules(checks_path):
            module_name = module_info.name
            module = importlib.import_module(f"scanner.checks.{module_name}")
            if hasattr(module, "run_check"):
                checks.append(module.run_check)
        return checks

    def run(self):
        results = []
        for check in self.checks:
            try:
                result = check(self.target_url)
                results.append(result)
            except Exception as e:
                results.append({
                    "name": check.__name__,
                    "status": "error",
                    "severity": "high",
                    "details": str(e),
                    "recommendation": "Check failed unexpectedly."
                })
        score_result = score_check(self.target_url, all_results=results)
        results.append(score_result)
        return results
