# NimbusTech Ticket Processor (Module 1)

Process a nightly ticket CSV export into a JSON report.

Run from the project directory:

```powershell
python -m ticket_processor.main --input data/tickets_raw.csv --output data/tickets_report.json
```

The script logs each processing step. It does not write a report when more than
10% of rows are invalid.
