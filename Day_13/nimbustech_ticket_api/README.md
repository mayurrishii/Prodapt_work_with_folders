# NimbusTech Ticket Processor (Module 1)

Process a nightly ticket CSV export into a JSON report.

Run from the project directory:

```powershell
python -m ticket_processor.main --input data/tickets_raw.csv --output data/tickets_report.json
```

The script logs each processing step. It does not write a report when more than
10% of rows are invalid.

## Module 2: Ticket API

After generating `data/tickets_report.json`, start the API from the project
directory:

```powershell
uvicorn ticket_api.main:app --reload
```

Open `http://127.0.0.1:8000/docs` to test the API routes. Ticket changes are
kept in memory while the server runs; they do not overwrite the JSON report.
