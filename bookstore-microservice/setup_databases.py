#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup_databases.py - Drop & recreate all microservice databases, then run migrations.

Run once to set up a clean database environment:
    py setup_databases.py

Requires: MySQL running on localhost:3306, password=paperrose
"""

import subprocess
import sys
import os

MYSQL = r"C:/Program Files/MySQL/MySQL Server 8.0/bin/mysql.exe"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASES = [
    "staff_db", "manager_db", "customer_db", "catalog_db", "book_db",
    "cart_db", "order_db", "ship_db", "pay_db", "comment_db", "recommender_db",
]

SERVICES = [
    ("staff-service",          "staff_db",       "staff"),
    ("manager-service",        "manager_db",     "manager"),
    ("customer-service",       "customer_db",    "customer"),
    ("catalog-service",        "catalog_db",     "catalog"),
    ("book-service",           "book_db",        "books"),
    ("cart-service",           "cart_db",        "cart"),
    ("order-service",          "order_db",       "orders"),
    ("ship-service",           "ship_db",        "shipping"),
    ("pay-service",            "pay_db",         "payment"),
    ("comment-rate-service",   "comment_db",     "comments"),
    ("recommender-ai-service", "recommender_db", "recommender"),
]

COMMON_ENV = {
    "DB_HOST": "localhost",
    "DB_USER": "root",
    "DB_PASSWORD": "paperrose",
    "DB_PORT": "3306",
}


def mysql_cmd(sql):
    result = subprocess.run(
        [MYSQL, "-u", "root", "-ppaperrose", "-e", sql],
        capture_output=True, text=True
    )
    return result.returncode == 0, result.stderr


def recreate_databases():
    print("[*] Dropping and recreating databases...")
    sql_parts = []
    for db in DATABASES:
        sql_parts.append(f"DROP DATABASE IF EXISTS `{db}`;")
        sql_parts.append(f"CREATE DATABASE `{db}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    sql = " ".join(sql_parts)
    ok, err = mysql_cmd(sql)
    if ok:
        print(f"  [OK] All {len(DATABASES)} databases recreated")
    else:
        print(f"  [FAIL] Error: {err}")
        sys.exit(1)


def run_migrations():
    print("\n[*] Running migrations for all services...\n")
    results = []
    for service_dir, db_name, app_name in SERVICES:
        svc_path = os.path.join(BASE_DIR, service_dir)
        if not os.path.exists(svc_path):
            print(f"  [SKIP] {service_dir}: directory not found")
            results.append((service_dir, "SKIPPED"))
            continue

        env = os.environ.copy()
        env.update(COMMON_ENV)
        env["DB_NAME"] = db_name

        # makemigrations
        r1 = subprocess.run(
            [sys.executable, "manage.py", "makemigrations", app_name],
            cwd=svc_path, env=env, capture_output=True, text=True
        )
        if r1.returncode != 0:
            print(f"  [FAIL] {service_dir} makemigrations:\n{r1.stderr[:500]}")
            results.append((service_dir, "FAIL-makemigrations"))
            continue

        # migrate
        r2 = subprocess.run(
            [sys.executable, "manage.py", "migrate"],
            cwd=svc_path, env=env, capture_output=True, text=True
        )
        if r2.returncode == 0:
            print(f"  [OK]   {service_dir:<30} -> {db_name}")
            results.append((service_dir, "OK"))
        else:
            print(f"  [FAIL] {service_dir} migrate:\n{r2.stderr[:500]}")
            results.append((service_dir, "FAIL-migrate"))

    print()
    print("=" * 55)
    print("  Migration Summary")
    print("=" * 55)
    for name, status in results:
        print(f"  {name:<30} {status}")
    print("=" * 55)


def main():
    print("=" * 55)
    print("  BookStore Microservices - Database Setup")
    print("=" * 55)
    print()

    print("[!] This will DROP and RECREATE these databases:")
    for db in DATABASES:
        print(f"     - {db}")
    print()
    ans = input("Continue? [y/N] ").strip().lower()
    if ans != "y":
        print("Cancelled.")
        sys.exit(0)

    print()
    recreate_databases()
    run_migrations()

    print()
    print("[DONE] Setup complete!")
    print()
    print("Next steps:")
    print("  1. Start services:    py run_local.py")
    print("  2. Insert test data:  py seed_data.py")
    print("  3. Open browser:      http://localhost:8000")
    print()


if __name__ == "__main__":
    main()
