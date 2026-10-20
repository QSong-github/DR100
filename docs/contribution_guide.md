# Contribution Guide

Thanks for considering a contribution to DR100. The registry grows through
community-curated additions and corrections.

## What you can contribute

1. **Add a new resource** (drug-centric / drug-related / auxiliary).
2. **Correct or enrich an annotation** on an existing record (e.g., update
   `update_cadence` when a resource releases a new version, add a `license`
   string, fix a `pathway` assignment).
3. **Add a demo notebook** showing how the registry helps an agent in a new
   case study.
4. **Improve the schema** (open an issue first to discuss).

## Process

### For a new resource

1. Open a [New Resource issue](../../issues/new?template=new_resource.md) using
   the template. The maintainers will confirm scope fit (drug-centric? indirect?
   auxiliary?) before code review.
2. Edit the appropriate registry file:
   `registry/drug_centric.json`, `registry/drug_related.json`, or
   `registry/auxiliary.json`.
3. Run the build script to regenerate the TSV mirror and re-validate:
   ```bash
   python scripts/build_registry.py
   ```
4. Commit both the `.json` and `.tsv` files, and submit a pull request.

### For an annotation correction

- Edit only the affected fields in the relevant `registry/*.json`.
- Update `data_quality` if the change resolves a `needs_review` flag.
- Note the change in `CHANGELOG.md` under `[Unreleased]`.
- Submit a pull request describing the source for the corrected value.

## Schema compliance

Every PR is validated against `schema/dr100_schema.json` by CI. Locally:

```bash
python -c "
import json
from pathlib import Path
from jsonschema import Draft7Validator
schema = json.loads(Path('schema/dr100_schema.json').read_text())
v = Draft7Validator(schema)
for fn in ['drug_centric', 'drug_related', 'auxiliary']:
    data = json.loads(Path(f'registry/{fn}.json').read_text())
    errs = [(rec.get('name'), e.message) for rec in data for e in v.iter_errors(rec)]
    assert not errs, errs
    print(f'{fn}: OK')
"
```

## Authoritativeness flag

Each record has a `data_quality` field:

- `"authoritative"` — the construction script matched the record's name exactly and
  accepted its annotations. This describes the construction process, not an
  independent validation of every field.
- `"needs_review"` — flagged for follow-up. Common reasons: an approximate or missing
  name match between source files, missing annotation axes, or a default-looking value.

When you correct a record, you may flip `needs_review` → `authoritative` if you
have a citable source for every populated field.

## Subcategory vocabulary

The `subcategory` field is a controlled vocabulary. For drug-centric resources,
the 17 values in use are those found in `registry/drug_centric.json`. Proposing a new
subcategory requires opening an issue first — we keep the vocabulary tight to
preserve the cross-resource analyses.

## Code style

- Python: PEP 8 + type hints. We use no formatter strictly, but match the
  existing style in `scripts/`.
- JSON: 2-space indent, sorted alphabetically by field name within each record
  (matches the build script's output).

## License

By contributing, you agree that:
- Data contributions are licensed under [CC BY 4.0](../LICENSE-DATA).
- Code contributions are licensed under [MIT](../LICENSE-CODE).
