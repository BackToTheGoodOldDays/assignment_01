#!/usr/bin/env python3
"""
run_local.py - Start all BookStore microservices locally with colored output.

Usage:
    python run_local.py              # Start all services
    python run_local.py migrate      # Run migrations for all services
    python run_local.py stop         # Stop all services (Ctrl+C)

Requirements:
    pip install colorama

Each service runs on its own port. Logs are color-coded per service.
"""

import subprocess
import threading
import sys
import os
import time
import signal

# Fix Windows console encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

try:
    from colorama import Fore, Style, init as colorama_init
    colorama_init()
    USE_COLOR = True
except ImportError:
    USE_COLOR = False

# ── Service definitions ──────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SERVICES = [
    {
        "name": "staff-service",
        "dir": "staff-service",
        "port": 8001,
        "color": Fore.CYAN if USE_COLOR else "",
        "env": {
            "DB_NAME": "staff_db",
            "JWT_SECRET": "staff-jwt-secret-local",
            "BOOK_SERVICE_URL": "http://localhost:8005",
        },
    },
    {
        "name": "manager-service",
        "dir": "manager-service",
        "port": 8002,
        "color": Fore.MAGENTA if USE_COLOR else "",
        "env": {
            "DB_NAME": "manager_db",
            "JWT_SECRET": "manager-jwt-secret-local",
            "BOOK_SERVICE_URL": "http://localhost:8005",
            "ORDER_SERVICE_URL": "http://localhost:8007",
            "CUSTOMER_SERVICE_URL": "http://localhost:8003",
        },
    },
    {
        "name": "customer-service",
        "dir": "customer-service",
        "port": 8003,
        "color": Fore.YELLOW if USE_COLOR else "",
        "env": {
            "DB_NAME": "customer_db",
            "JWT_SECRET": "customer-jwt-secret-local",
            "CART_SERVICE_URL": "http://localhost:8006",
        },
    },
    {
        "name": "catalog-service",
        "dir": "catalog-service",
        "port": 8004,
        "color": Fore.GREEN if USE_COLOR else "",
        "env": {
            "DB_NAME": "catalog_db",
        },
    },
    {
        "name": "book-service",
        "dir": "book-service",
        "port": 8005,
        "color": Fore.BLUE if USE_COLOR else "",
        "env": {
            "DB_NAME": "book_db",
            "CATALOG_SERVICE_URL": "http://localhost:8004",
        },
    },
    {
        "name": "cart-service",
        "dir": "cart-service",
        "port": 8006,
        "color": Fore.RED if USE_COLOR else "",
        "env": {
            "DB_NAME": "cart_db",
            "BOOK_SERVICE_URL": "http://localhost:8005",
        },
    },
    {
        "name": "order-service",
        "dir": "order-service",
        "port": 8007,
        "color": Fore.WHITE if USE_COLOR else "",
        "env": {
            "DB_NAME": "order_db",
            "CART_SERVICE_URL": "http://localhost:8006",
            "BOOK_SERVICE_URL": "http://localhost:8005",
            "PAY_SERVICE_URL": "http://localhost:8009",
            "SHIP_SERVICE_URL": "http://localhost:8008",
        },
    },
    {
        "name": "ship-service",
        "dir": "ship-service",
        "port": 8008,
        "color": Fore.LIGHTCYAN_EX if USE_COLOR else "",
        "env": {
            "DB_NAME": "ship_db",
        },
    },
    {
        "name": "pay-service",
        "dir": "pay-service",
        "port": 8009,
        "color": Fore.LIGHTGREEN_EX if USE_COLOR else "",
        "env": {
            "DB_NAME": "pay_db",
        },
    },
    {
        "name": "comment-rate-service",
        "dir": "comment-rate-service",
        "port": 8010,
        "color": Fore.LIGHTYELLOW_EX if USE_COLOR else "",
        "env": {
            "DB_NAME": "comment_db",
            "BOOK_SERVICE_URL": "http://localhost:8005",
        },
    },
    {
        "name": "recommender-ai-service",
        "dir": "recommender-ai-service",
        "port": 8011,
        "color": Fore.LIGHTMAGENTA_EX if USE_COLOR else "",
        "env": {
            "DB_NAME": "recommender_db",
            "BOOK_SERVICE_URL": "http://localhost:8005",
            "ORDER_SERVICE_URL": "http://localhost:8007",
        },
    },
    {
        "name": "api-gateway",
        "dir": "api-gateway",
        "port": 8000,
        "color": Fore.LIGHTBLUE_EX if USE_COLOR else "",
        "env": {
            "STAFF_SERVICE_URL": "http://localhost:8001",
            "MANAGER_SERVICE_URL": "http://localhost:8002",
            "CUSTOMER_SERVICE_URL": "http://localhost:8003",
            "CATALOG_SERVICE_URL": "http://localhost:8004",
            "BOOK_SERVICE_URL": "http://localhost:8005",
            "CART_SERVICE_URL": "http://localhost:8006",
            "ORDER_SERVICE_URL": "http://localhost:8007",
            "SHIP_SERVICE_URL": "http://localhost:8008",
            "PAY_SERVICE_URL": "http://localhost:8009",
            "COMMENT_SERVICE_URL": "http://localhost:8010",
            "RECOMMENDER_SERVICE_URL": "http://localhost:8011",
        },
    },
]

# Common env for all services
COMMON_ENV = {
    "DB_HOST": "localhost",
    "DB_USER": "root",
    "DB_PASSWORD": "paperrose",
    "DB_PORT": "3306",
}

RESET = Style.RESET_ALL if USE_COLOR else ""
processes = []


def get_service_env(service):
    """Build environment variables for a service."""
    env = os.environ.copy()
    env.update(COMMON_ENV)
    env.update(service.get("env", {}))
    return env


def run_migrations(service):
    """Run Django migrations for a service."""
    service_dir = os.path.join(BASE_DIR, service["dir"])
    if not os.path.exists(service_dir):
        print(f"[WARN] {service['name']}: directory not found, skipping")
        return False

    env = get_service_env(service)
    color = service["color"]
    label = f"[{service['name']}]"

    print(f"{color}{label} Running migrations...{RESET}")

    result = subprocess.run(
        [sys.executable, "manage.py", "migrate", "--run-syncdb"],
        cwd=service_dir,
        env=env,
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print(f"{color}{label} Migrations OK{RESET}")
    else:
        print(f"{color}{label} Migration error:\n{result.stderr}{RESET}")
    return result.returncode == 0


def stream_output(process, service):
    """Stream process output with color prefix."""
    color = service["color"]
    label = f"[{service['name']}:{service['port']}]"

    for line in iter(process.stdout.readline, ""):
        print(f"{color}{label} {line.rstrip()}{RESET}", flush=True)

    for line in iter(process.stderr.readline, ""):
        print(f"{color}{label} {line.rstrip()}{RESET}", flush=True)


def start_service(service):
    """Start a single Django service."""
    service_dir = os.path.join(BASE_DIR, service["dir"])
    if not os.path.exists(service_dir):
        print(f"[WARN] {service['name']}: directory '{service_dir}' not found, skipping.")
        return None

    env = get_service_env(service)
    port = service["port"]

    process = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", f"0.0.0.0:{port}", "--noreload"],
        cwd=service_dir,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    thread = threading.Thread(target=stream_output, args=(process, service), daemon=True)
    thread.start()

    return process


def print_service_table():
    """Print a table of all services and their ports."""
    print("\n" + "=" * 60)
    print("  BookStore Microservices")
    print("=" * 60)
    print(f"  {'Service':<30} {'Port':<8} {'URL'}")
    print("-" * 60)
    for svc in SERVICES:
        color = svc["color"]
        print(f"  {color}{svc['name']:<30} {svc['port']:<8} http://localhost:{svc['port']}{RESET}")
    print("=" * 60)
    print("  API Gateway (Web UI): http://localhost:8000")
    print("=" * 60 + "\n")


def migrate_all():
    """Run migrations for all services."""
    print("\n[*] Running migrations for all services...\n")
    results = []
    for service in SERVICES:
        ok = run_migrations(service)
        results.append((service["name"], ok))
    print("\n" + "=" * 60)
    print("  Migration Results")
    print("=" * 60)
    for name, ok in results:
        status = "[OK]  " if ok else "[FAIL]"
        print(f"  {name:<35} {status}")
    print("=" * 60 + "\n")


def start_all():
    """Start all services."""
    print_service_table()
    print("[*] Starting all services... (Press Ctrl+C to stop)\n")

    for service in SERVICES:
        proc = start_service(service)
        if proc:
            processes.append((service, proc))
            print(f"  [OK] {service['name']} started on port {service['port']}")
            time.sleep(0.3)

    print(f"\n  All services started. Web UI at: http://localhost:8000\n")

    def shutdown(signum, frame):
        print("\n\n[*] Stopping all services...")
        for svc, proc in processes:
            proc.terminate()
            print(f"  Stopped {svc['name']}")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Keep main thread alive
    while True:
        time.sleep(1)
        # Check if all processes died
        all_dead = all(proc.poll() is not None for _, proc in processes)
        if all_dead:
            print("\n[!] All services stopped.")
            break


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "start"

    if cmd == "migrate":
        migrate_all()
    elif cmd == "start":
        start_all()
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: python run_local.py [start|migrate]")
        sys.exit(1)
