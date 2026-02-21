# Wahapedia CSV fields for 40K Army Book Reference

The **40K Army Book Reference** view reads from existing `waha_*` tables. The Wahapedia source CSVs in `data/wahapedia/` contain additional columns that are **not** currently in the DB (or not fully used). Hydrating these would make the 40K reference richer and closer to the OPR Army Book (unit lore, role grouping, loadout summary).

## Datasheets.csv — columns not (or only partly) in `waha_datasheets`

| CSV column        | Possible DB use                    | Notes |
|-------------------|------------------------------------|--------|
| `legend`          | Unit fluff / background text       | Long text; could be `waha_datasheets.legend` (TEXT). |
| `role`            | Official role (Characters, Battleline, Other) | Cleaner grouping than inferring from Keywords. Add `waha_datasheets.role` (VARCHAR). |
| `loadout`         | Default equipment summary          | Short; could be `waha_datasheets.loadout` (TEXT). |
| `transport`       | Transport capacity / rules        | e.g. "This model has a transport capacity of 6 …". |
| `damaged_w`       | Degraded profile (e.g. "1-5")       | For vehicles. |
| `damaged_description` | Degraded rules text             | "While this model has 1-5 wounds remaining …". |
| `link`            | Wahapedia URL                      | Optional; for "View on Wahapedia" link. |

**Suggested migration:** Add to `waha_datasheets`:

- `legend` TEXT NULL  
- `role` VARCHAR(50) NULL  
- `loadout` TEXT NULL  
- `transport` TEXT NULL  
- `damaged_w` VARCHAR(50) NULL  
- `damaged_description` TEXT NULL  

Then a one-off or recurring script: read `data/wahapedia/Datasheets.csv` (or `Cleaned_CSVs/Datasheets_Clean.csv`), match by `id` → `waha_datasheet_id`, UPDATE these columns. After that, the 40K Army Book Reference can show unit legend and group by `role` instead of inferring from Keywords.

## Detachments.csv

- `legend`, `type` — already in `waha_detachments` in the schema. Ensure your hydration populates them from the CSV.

## Other CSVs

- **Datasheets_abilities**, **Datasheets_wargear**, **Datasheets_options** — already have corresponding `waha_datasheets_*` tables; ensure CSV import keeps them in sync.
- **Stratagems**, **Enhancements**, **Detachment_abilities** — same idea; reference view can keep using existing views/tables once data is present.

## Summary

- **Current 40K Army Book Reference:** Uses existing DB (faction, detachment legend from `waha_detachments`, datasheets, abilities, wargear, options). Role grouping uses `waha_datasheets.role` when present, else inferred from Keywords.
- **Implemented:** Migration `ProxyForge/migrations/add_waha_datasheets_extra.sql` adds `legend`, `role`, `loadout`, `transport`, `damaged_w`, `damaged_description`, `link` to `waha_datasheets`. Script `scripts/wahapedia/hydrate_waha_datasheets_extra.py` reads `data/wahapedia/Datasheets.csv` and updates those columns by `waha_datasheet_id`. After running the migration and hydrator, the 40K Army Book Reference shows unit lore (legend), loadout, transport, damaged profile, and groups by official role when present.
