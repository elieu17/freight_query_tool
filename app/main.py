from datetime import date
from pathlib import Path
import csv
import io

from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from app.db import SessionLocal
from app.queries import search_rates, find_ports


app = FastAPI(title="Rate Query")
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/")
def home():
    return {"status": "Render is working"}


@app.get("/rates", response_class=HTMLResponse)
def rates_page(
    request: Request,
    origin: str,
    destination: str,
    ship_date: date,
    contract_type: str,                       # make required if you want
    equipment_type: str | None = None,        # optional => all equipment
    dg: bool = Query(False),
    limit: int = 50,
):
    db = SessionLocal()
    try:
        results = search_rates(
            db=db,
            origin=origin,
            destination=destination,
            equipment_type=equipment_type,
            ship_date=ship_date,
            contract_type=contract_type,
            dg=dg,
            limit=limit,
        )

        q = {
            "origin": origin,
            "destination": destination,
            "equipment_type": equipment_type or "",
            "ship_date": ship_date.isoformat(),
            "contract_type": contract_type or "",
            "dg": dg,
        }

        return templates.TemplateResponse(
            "index.html",
            {"request": request, "results": results, "error": None, "q": q}
        )
    finally:
        db.close()


@app.get("/api/rates")
def rates_api(
    origin: str,
    destination: str,
    ship_date: date,
    contract_type: str,
    equipment_type: str | None = None,
    dg: bool = Query(False),
    limit: int = 50,
):
    db = SessionLocal()
    try:
        results = search_rates(
            db=db,
            origin=origin,
            destination=destination,
            equipment_type=equipment_type,
            ship_date=ship_date,
            contract_type=contract_type,
            dg=dg,
            limit=limit,
        )
        return {"count": len(results), "items": [dict(r) for r in results]}
    finally:
        db.close()


@app.get("/api/ports")
def ports_api(q: str, limit: int = 10):
    db = SessionLocal()
    try:
        results = find_ports(db, q, limit)
        items = [{
            "unlocode": r["unlocode"],
            "label": f'{r["unlocode"]} — {r["name"]}'
                     + (f', {r["subdivision"]}' if r["subdivision"] else "")
                     + (f', {r["country"]}' if r["country"] else "")
        } for r in results]
        return {"count": len(items), "items": items}
    finally:
        db.close()

@app.get("/download")
def download_csv(
    origin: str,
    destination: str,
    ship_date: date,
    contract_type: str,
    equipment_type: str | None = None,
    dg: bool = Query(False),
    limit: int = 5000,
):
    db = SessionLocal()
    try:
        results = search_rates(
            db=db,
            origin=origin,
            destination=destination,
            equipment_type=equipment_type,
            ship_date=ship_date,
            contract_type=contract_type,
            dg=dg,
            limit=limit,
        )

        buf = io.StringIO()
        writer = csv.writer(buf)

        headers = [
            "origin_unlocode", "origin_name",
            "destination_unlocode", "destination_name",
            "trade", "equipment_type", "contract_type",
            "currency", "base_rate", "bunker_rate",
        ]
        if dg:
            headers.append("dg_charge")
        headers += ["all_in_ocean", "service_level", "effective_date", "expiry_date"]

        writer.writerow(headers)

        for r in results:
            row = [
                r.get("origin_unlocode"), r.get("origin_name"),
                r.get("destination_unlocode"), r.get("destination_name"),
                r.get("trade"), r.get("equipment_type"), r.get("contract_type"),
                r.get("currency"), r.get("base_rate"), r.get("bunker_rate"),
            ]
            if dg:
                row.append(r.get("dg_charge"))
            row += [r.get("all_in_ocean"), r.get("service_level"), r.get("effective_date"), r.get("expiry_date")]
            writer.writerow(row)

        buf.seek(0)
        filename = f"rates_{ship_date.isoformat()}_{contract_type}_{equipment_type or 'ALL'}{'_DG' if dg else ''}.csv"

        return StreamingResponse(
            iter([buf.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    finally:
        db.close()
