# Odoo 15 CE to ERPNext 16 Migrator

A generic, robust migration toolkit to extract and migrate Master and Transaction data from **Odoo 15 Community Edition** to **ERPNext 16**.

## Features

- **Decoupled & Generic:** Migrates to standard ERPNext doctypes (`Customer`, `Supplier`, `Item`, `Item Group`, `UOM`, `Sales Invoice`, `Payment Entry`, `Account`).
- **Odoo XML-RPC Integration:** Secure, non-invasive extraction directly from live or staging Odoo instances.
- **Idempotent Sync:** Attaches unique `custom_odoo_id` tracking fields across ERPNext documents to ensure repeated syncs update rather than duplicate records.
- **Extensible Hooks:** Emits standard Frappe hooks (e.g. `on_odoo_partner_migrated`) allowing downstream domain-specific apps or custom integrations to react and generate secondary records.
- **Migration Logs & Audit Trail:** Full logging of synced records, skips, and error payloads via `Odoo Migration Log`.
- **Custom Mapping Rules:** Map Odoo Chart of Accounts, Taxes, and Payment Methods to ERPNext ledgers via `Odoo Mapping Rule`.

## Included DocTypes

1. **Odoo Migration Settings** (Single):
   - Server URL, database, credentials, batch size, and target company.
   - Connection test action.
2. **Odoo Mapping Rule**:
   - Explicit mapping between Odoo accounts/taxes and ERPNext target records.
3. **Odoo Migration Log**:
   - Audit trail capturing source Odoo ID, target ERPNext DocType/Name, and sync error details.

## CLI Commands

```bash
bench --site [site-name] odoo test-connection
bench --site [site-name] odoo sync-uom
bench --site [site-name] odoo sync-categories
bench --site [site-name] odoo sync-items --limit 50
bench --site [site-name] odoo sync-partners --limit 50
```

## License

MIT
