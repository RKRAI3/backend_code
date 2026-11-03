"""One-off migration from the single-country schema to the multi-country schema.

Run it once per existing database, BEFORE starting the new app version:

    python -m scripts.migrate_multi_country --code TH --name Thailand \
        --currency-code THB --currency-symbol "฿" --package-name "Full Package"

It is idempotent: it only adds what is missing, and existing rows without a country
are assigned to the country given on the command line (created if it doesn't exist).
Defaults for tax rate / currency symbol / business name / alert emails come from .env.
"""
import argparse
import os
import sys

from flask import Flask
from sqlalchemy import inspect, text

from app import db
from environment import DATABASE_URL, TAX_RATE, CURRENCY, FROM_NAME, ADMIN_ID

# (table, column, DDL type, extra DDL)
NEW_COLUMNS = [
    ('countries', 'package_price', 'DECIMAL(14, 3)', 'NULL'),
    ('users', 'role', 'VARCHAR(20)', "NOT NULL DEFAULT 'staff'"),
    ('users', 'country_id', 'VARCHAR(36)', 'NULL'),
    ('products', 'country_id', 'VARCHAR(36)', 'NULL'),
    ('receipts', 'country_id', 'VARCHAR(36)', 'NULL'),
    ('receipts', 'currency_code', 'VARCHAR(3)', 'NULL'),
    ('receipts', 'tax_rate', 'DECIMAL(6, 4)', 'NULL'),
]

NEW_INDEXES = [
    ('ix_users_country_id', 'users', 'country_id'),
    ('ix_products_country_id', 'products', 'country_id'),
    ('ix_receipts_country_id', 'receipts', 'country_id'),
]

# Money columns widened to 3 decimals (e.g. Kuwaiti dinar). SQLite doesn't enforce scale.
WIDEN_COLUMNS = [
    ('products', 'unit_price', 'DECIMAL(12, 3)'),
    ('receipt_items', 'std_price', 'DECIMAL(12, 3)'),
    ('receipt_items', 'vendor_price', 'DECIMAL(12, 3)'),
    ('receipt_items', 'total_std_price', 'DECIMAL(14, 3)'),
    ('receipt_items', 'total_vend_price', 'DECIMAL(14, 3)'),
    ('receipts', 'package_amt', 'DECIMAL(14, 3)'),
    ('receipts', 'total_std_amount', 'DECIMAL(14, 3)'),
    ('receipts', 'total_vend_amount', 'DECIMAL(14, 3)'),
    ('receipts', 'tax_amount', 'DECIMAL(14, 3)'),
    ('receipts', 'gross_amount', 'DECIMAL(14, 3)'),
]


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--code', required=True, help='ISO country code for existing data, e.g. TH')
    parser.add_argument('--name', required=True, help='Country name, e.g. Thailand')
    parser.add_argument('--currency-code', required=True, help='ISO currency code, e.g. THB')
    parser.add_argument('--currency-symbol', default=CURRENCY)
    parser.add_argument('--currency-decimals', type=int, default=2)
    parser.add_argument('--tax-rate', default=TAX_RATE or '0')
    parser.add_argument('--package-name', default=None, help='e.g. "Full Package"')
    parser.add_argument('--package-price', default=None, help='Fixed package total, e.g. 1000')
    parser.add_argument('--receipt-prefix', default='IN')
    parser.add_argument('--business-name', default=FROM_NAME)
    parser.add_argument('--alert-emails', default=os.getenv('ALERT_EMAIL_RECIPIENTS', ''))
    return parser.parse_args()


def add_columns(conn, inspector):
    for table, column, ddl_type, extra in NEW_COLUMNS:
        existing = {c['name'] for c in inspector.get_columns(table)}
        if column not in existing:
            print(f"  + {table}.{column}")
            conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {ddl_type} {extra}"))


def add_indexes(conn, inspector):
    for name, table, column in NEW_INDEXES:
        if name not in {i['name'] for i in inspector.get_indexes(table)}:
            print(f"  + index {name}")
            conn.execute(text(f"CREATE INDEX {name} ON {table} ({column})"))


def widen_columns(conn, dialect):
    if dialect == 'mysql':
        stmt = "ALTER TABLE {t} MODIFY COLUMN {c} {ty} NOT NULL"
    elif dialect == 'postgresql':
        stmt = "ALTER TABLE {t} ALTER COLUMN {c} TYPE {ty}"
    else:
        print(f"  (skipping decimal widening on {dialect})")
        return
    for table, column, ddl_type in WIDEN_COLUMNS:
        conn.execute(text(stmt.format(t=table, c=column, ty=ddl_type)))
    print("  ~ money columns widened to 3 decimals")


def main():
    args = parse_args()

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    db.init_app(app)
    import models  # noqa: F401  register all tables
    from models.country import Country
    from models.user import SUPER_ADMIN, COUNTRY_ADMIN, STAFF

    with app.app_context():
        print("1. Creating new tables")
        db.create_all()  # creates `countries`; existing tables are left untouched

        print("2. Adding new columns")
        with db.engine.begin() as conn:
            inspector = inspect(conn)
            add_columns(conn, inspector)
            add_indexes(conn, inspect(conn))
            widen_columns(conn, db.engine.dialect.name)

        print(f"3. Default country {args.code}")
        country = Country.query.filter_by(code=args.code.upper()).first()
        if not country:
            country = Country(
                code=args.code.upper(),
                name=args.name,
                currency_code=args.currency_code.upper(),
                currency_symbol=args.currency_symbol,
                currency_decimals=args.currency_decimals,
                tax_rate=args.tax_rate,
                package_name=args.package_name,
                package_price=args.package_price,
                receipt_prefix=args.receipt_prefix,
                business_name=args.business_name,
                alert_emails=args.alert_emails or None,
            )
            db.session.add(country)
            db.session.commit()
            print(f"  + created {country.name} ({country.country_id})")
        else:
            print(f"  = exists ({country.country_id})")
            # Fill in a package price added after the country was first migrated
            if args.package_price is not None and country.package_price is None:
                country.package_price = args.package_price
                db.session.commit()
                print(f"  ~ package_price set to {args.package_price}")

        print("4. Backfilling existing rows")
        params = {'cid': country.country_id, 'cur': country.currency_code, 'tax': str(country.tax_rate),
                  'admin': ADMIN_ID or '', 'super': SUPER_ADMIN, 'cadmin': COUNTRY_ADMIN, 'staff': STAFF}
        statements = [
            # bootstrap admin from .env manages every country
            "UPDATE users SET role = :super, country_id = NULL WHERE email = :admin",
            # other existing admins become admins of the default country
            "UPDATE users SET role = :cadmin WHERE is_admin = :true AND role = :staff AND email <> :admin",
            "UPDATE users SET country_id = :cid WHERE country_id IS NULL AND role <> :super",
            "UPDATE products SET country_id = :cid WHERE country_id IS NULL",
            "UPDATE receipts SET country_id = :cid WHERE country_id IS NULL",
            "UPDATE receipts SET currency_code = :cur WHERE currency_code IS NULL AND country_id = :cid",
            "UPDATE receipts SET tax_rate = :tax WHERE tax_rate IS NULL AND country_id = :cid",
        ]
        for stmt in statements:
            result = db.session.execute(text(stmt), {**params, 'true': True})
            print(f"  {result.rowcount:>6} rows: {stmt.split(' WHERE')[0]}")
        db.session.commit()

    print("Done.")


if __name__ == '__main__':
    sys.exit(main())
