"""
run.py
Cross-platform entry point for running the test suite.

Usage:
    python run.py                        # Run all tests
    python run.py --suite auth           # Run one suite
    python run.py --headed               # Run with visible browser
    python run.py --browser firefox      # Use Firefox
    python run.py --allure               # Also generate Allure results
    python run.py --parallel 4          # Run 4 tests in parallel
    python run.py --suite checkout --headed --browser firefox

Works identically on Windows, macOS, and Linux.
No shell scripts, no Makefile, no OS-specific commands needed.
"""

import argparse
import os
import platform
import subprocess
import sys
from pathlib import Path


# ── Helpers ───────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent


def ensure_reports_dir():
    """Create reports/ and screenshots/ dirs if they don't exist yet."""
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "screenshots").mkdir(exist_ok=True)


def ensure_env_file():
    """Copy .env.example → .env if .env doesn't exist yet."""
    env_file = ROOT / ".env"
    example_file = ROOT / ".env.example"
    if not env_file.exists() and example_file.exists():
        import shutil
        shutil.copy(example_file, env_file)
        print("[run.py] Created .env from .env.example")


def print_banner(args):
    print("\n" + "=" * 60)
    print("  SauceDemo QA Automation Framework")
    print(f"  OS       : {platform.system()} {platform.release()}")
    print(f"  Python   : {sys.version.split()[0]}")
    print(f"  Browser  : {args.browser}")
    print(f"  Headless : {not args.headed}")
    print(f"  Suite    : {args.suite or 'ALL'}")
    print("=" * 60 + "\n")


def open_report():
    """Open the HTML report in the default browser, cross-platform."""
    report = ROOT / "reports" / "report.html"
    if not report.exists():
        print("[run.py] No report found at reports/report.html")
        return
    system = platform.system()
    if system == "Windows":
        os.startfile(str(report))
    elif system == "Darwin":
        subprocess.run(["open", str(report)])
    else:
        subprocess.run(["xdg-open", str(report)])


# ── Argument parsing ──────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="Run the SauceDemo QA test suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py
  python run.py --suite auth
  python run.py --suite checkout --headed
  python run.py --browser firefox --parallel 4
  python run.py --allure
        """,
    )
    parser.add_argument(
        "--suite",
        choices=["auth", "catalog", "cart", "checkout", "performance"],
        default=None,
        help="Run only a specific test suite (default: all)",
    )
    parser.add_argument(
        "--browser",
        choices=["chrome", "firefox"],
        default="chrome",
        help="Browser to use (default: chrome)",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Run with a visible browser window (default: headless)",
    )
    parser.add_argument(
        "--allure",
        action="store_true",
        help="Also write Allure results to allure-results/",
    )
    parser.add_argument(
        "--parallel",
        type=int,
        default=1,
        metavar="N",
        help="Run N tests in parallel (requires pytest-xdist)",
    )
    parser.add_argument(
        "--open-report",
        action="store_true",
        help="Open the HTML report in your browser after the run",
    )
    return parser.parse_args()


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    args = parse_args()
    ensure_reports_dir()
    ensure_env_file()
    print_banner(args)

    # ── Set environment variables for this run ────────────────────────────────
    env = os.environ.copy()
    env["BROWSER"] = args.browser
    env["HEADLESS"] = "false" if args.headed else "true"

    # Pass through CHROMEDRIVER_PATH if already set in the environment
    # (e.g. set by CI or by the user manually)
    if os.environ.get("CHROMEDRIVER_PATH"):
        env["CHROMEDRIVER_PATH"] = os.environ["CHROMEDRIVER_PATH"]

    # ── Build pytest command ──────────────────────────────────────────────────
    cmd = [sys.executable, "-m", "pytest"]

    # Target: specific suite file or all tests
    if args.suite:
        cmd.append(str(ROOT / "src" / "tests" / f"test_{args.suite}.py"))

    # Parallel execution
    if args.parallel > 1:
        cmd += ["-n", str(args.parallel)]

    # Allure results (optional — doesn't break if Allure CLI isn't installed)
    if args.allure:
        cmd += ["--alluredir", str(ROOT / "allure-results")]

    # ── Run ───────────────────────────────────────────────────────────────────
    print(f"[run.py] Command: {' '.join(cmd)}\n")
    result = subprocess.run(cmd, env=env, cwd=str(ROOT))

    # ── Post-run ──────────────────────────────────────────────────────────────
    print(f"\n[run.py] HTML report → {ROOT / 'reports' / 'report.html'}")

    if args.open_report:
        open_report()

    if args.allure:
        print(f"[run.py] Allure results → {ROOT / 'allure-results'}")
        print("[run.py] To view: allure serve allure-results")

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
