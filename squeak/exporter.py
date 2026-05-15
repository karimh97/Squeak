"""CSV export: per-trial files and an append-only session master sheet."""

import csv
from datetime import datetime
from pathlib import Path

from .scorer import Scorer


def export_trial(path: Path, meta: dict, scorer: Scorer) -> None:
    """Write a detailed per-trial CSV (metadata + summary + DI + event log)."""
    stats = scorer.stats()
    total = sum(s.total_time for s in stats)
    with path.open('w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['# Rodent Object Exploration Scorer'])
        w.writerow(['# Exported', datetime.now().isoformat(timespec='seconds')])
        w.writerow([])
        w.writerow(['Metadata'])
        for k, v in meta.items():
            w.writerow([k, v])
        w.writerow(['trial_duration_s_elapsed', f'{scorer.now():.3f}'])
        if scorer.duration is not None:
            w.writerow(['trial_duration_s_target', f'{scorer.duration:.3f}'])
        w.writerow([])

        w.writerow(['Summary'])
        w.writerow(['object', 'total_seconds', 'bouts', 'mean_bout_seconds'])
        for s in stats:
            w.writerow([s.name, f'{s.total_time:.3f}', s.bouts, f'{s.mean_bout:.3f}'])
        w.writerow(['TOTAL', f'{total:.3f}', sum(s.bouts for s in stats), ''])
        w.writerow([])

        if len(stats) == 2 and total > 0:
            a, b = stats
            di = (b.total_time - a.total_time) / total
            w.writerow(['Discrimination Index'])
            w.writerow(['formula', f'({b.name} - {a.name}) / total'])
            w.writerow(['DI', f'{di:.4f}'])
            w.writerow([f'preference_{b.name}', f'{(b.total_time/total):.4f}'])
            w.writerow([f'preference_{a.name}', f'{(a.total_time/total):.4f}'])
            w.writerow([])

        w.writerow(['Event log'])
        w.writerow(['t_seconds', 'object', 'event'])
        for e in scorer.events:
            w.writerow([f'{e.t:.3f}', e.object_name, e.event_type])


def append_to_master(path: Path, meta: dict, scorer: Scorer) -> None:
    """Append one row to a session-wide CSV. Header expands as new fields appear."""
    stats = scorer.stats()
    total = sum(s.total_time for s in stats)

    row: dict = {}
    row.update({k: str(v) for k, v in meta.items()})
    row['trial_duration_s'] = f'{scorer.now():.3f}'
    row['total_exploration_s'] = f'{total:.3f}'
    for s in stats:
        row[f'{s.name}_time_s'] = f'{s.total_time:.3f}'
        row[f'{s.name}_bouts'] = str(s.bouts)
    if len(stats) == 2 and total > 0:
        a, b = stats
        row['DI'] = f'{((b.total_time - a.total_time) / total):.4f}'
        row['DI_formula'] = f'({b.name} - {a.name}) / total'
    row['exported_at'] = datetime.now().isoformat(timespec='seconds')

    existing_rows: list[dict] = []
    existing_fields: list[str] = []
    if path.exists():
        with path.open('r', newline='') as f:
            r = csv.DictReader(f)
            existing_fields = list(r.fieldnames or [])
            existing_rows = list(r)

    fields = list(existing_fields)
    for k in row:
        if k not in fields:
            fields.append(k)

    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in existing_rows:
            w.writerow({k: r.get(k, '') for k in fields})
        w.writerow({k: row.get(k, '') for k in fields})
