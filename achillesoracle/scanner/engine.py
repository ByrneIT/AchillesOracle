import importlib
import pkgutil
from achillesoracle.scanner.checks import __path__ as checks_path


class ScannerEngine:
    def __init__(self, target_url):
        self.target_url = target_url
        self.checks = self._load_checks()

    def _load_checks(self):
        checks = []
        for module_info in pkgutil.iter_modules(checks_path):
            module_name = module_info.name
            # Skip the aggregator/scoring module so it isn't executed as a normal check
            if module_name == "security_score_check":
                continue

            try:
                module = importlib.import_module(
                    f"achillesoracle.scanner.checks.{module_name}")
                if hasattr(module, "run_check"):
                    checks.append(module.run_check)
            except Exception as e:
                # If a module fails to import, include a soft-fail placeholder
                def _placeholder(target_url, module_name=module_name, err=str(e)):
                    return {
                        "name": f"{module_name} (load failed)",
                        "status": "soft-fail",
                        "severity": "low",
                        "details": f"Module import failed: {err}",
                        "recommendation": "Module skipped; treated as neutral."
                    }

                checks.append(_placeholder)
                continue

        return checks

    def run(self):
        try:
            results = []
            for check in self.checks:
                try:
                    result = check(self.target_url)
                    if not isinstance(result, dict):
                        results.append({
                            "name": getattr(check, "__name__", "Unnamed Check"),
                            "status": "soft-fail",
                            "severity": "low",
                            "details": "Check returned non-dict result; treated as neutral.",
                            "recommendation": "Ensure check returns a dict with at least 'name', 'status', and 'severity'."
                        })
                    else:
                        results.append(result)
                except Exception as e:
                    results.append({
                        "name": getattr(check, "__name__", "Unnamed Check"),
                        "status": "soft-fail",
                        "severity": "low",
                        "details": f"Check raised exception: {e}",
                        "recommendation": "Check failed; treated as neutral."
                    })

            # Attempt to import and run the scoring module; fall back to a simple internal score if it fails
            try:
                from achillesoracle.scanner.checks.security_score_check import run_check as score_check
                score_result = score_check(
                    self.target_url, all_results=results)
            except Exception as e:
                total = max(1, len(results))
                passed = sum(1 for r in results if r.get("status") == "pass")
                raw_score = int(round((passed / total) * 100))
                if raw_score >= 90:
                    grade = "A"
                elif raw_score >= 80:
                    grade = "B"
                elif raw_score >= 70:
                    grade = "C"
                elif raw_score >= 60:
                    grade = "D"
                else:
                    grade = "F"

                if raw_score >= 80:
                    overall_status = "pass"
                    overall_severity = "low"
                elif raw_score >= 60:
                    overall_status = "warn"
                    overall_severity = "medium"
                else:
                    overall_status = "error"
                    overall_severity = "high"

                details = f"Score: {raw_score}/100 -- Fallback score computed after scoring failure."
                score_result = {
                    "name": "Security Score",
                    "status": overall_status,
                    "severity": overall_severity,
                    "score": raw_score,
                    "grade": grade,
                    "details": details,
                    "breakdown": [],
                    "recommendation": "Scoring subsystem failed; fallback score used."
                }

            results.append(score_result)
            return results

        except Exception as e:
            # Global safety net: never raise from run(); return a neutral soft-fail result
            return [{
                "name": "ScannerEngine",
                "status": "soft-fail",
                "severity": "low",
                "details": f"Scanner failed unexpectedly: {e}",
                "recommendation": "Scan could not be completed; treated as neutral."
            }]
