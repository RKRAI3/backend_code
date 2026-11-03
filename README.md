# backend_code
pip install pylint, seed-isort-config,black,bandit,autopep8,flake8,isort,semgrep
pip install pre-commit

## Multi-country setup

One deployment serves every country. Currency, tax, package name, receipt prefix,
business name and alert emails are stored per country in the `countries` table and
managed from the UI; they are no longer read from `.env` or hardcoded.

### Roles
| Role | Can do |
|---|---|
| `super_admin` | Manage countries; manage users/services in any country (pass `country_id`) |
| `country_admin` | Manage users and services of their own country; generate receipts |
| `staff` | Generate receipts with their own country's services |

The `.env` admin (`ADMIN_ID`) is created as `super_admin` on first start.

### Upgrading an existing database
Run once per existing database, **before** starting the new version:

```
python -m scripts.migrate_multi_country --code TH --name Thailand \
    --currency-code THB --currency-symbol "฿" --package-name "Full Package" \
    --package-price 1000 --business-name "EASY VISA"
```

It adds the new columns, widens money columns to 3 decimals (MySQL/PostgreSQL),
and assigns existing users/services/receipts to that country. It is safe to re-run.

### API for the frontend
- `POST /api/auth/login` → `data.user` now includes `role`, `country_id` and `country`
  (`currency_symbol`, `currency_decimals`, `package_name`, `package_price`, `tax_rate`, ...). Use these to
  format amounts and show the package option. `GET /api/auth/me` returns the same.
- `GET/POST /api/countries/`, `GET/PUT/DELETE /api/countries/<id>` — super admin only.
  `DELETE` deactivates (data is kept, the country's users are locked out).
- `POST /api/users/createuser` accepts `role` and `country_id`
  (country admins can omit `country_id`; it defaults to their own).
- Services, receipts, users and dashboard endpoints are automatically limited to the
  logged-in user's country. A super admin passes `?country_id=<id>` (or `country_id` in
  the JSON body); it is required for creating services/receipts and for the dashboard.
- `GET /api/receipts/get-receipt/<id>` includes `currency_symbol`, `currency_decimals`
  and `business_name` for printing.
- `POST /api/auth/register` is disabled; admins create accounts.
