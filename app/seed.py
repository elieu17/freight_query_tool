import csv
from datetime import date
from decimal import Decimal
from app.db import engine, SessionLocal, Base
from app.models import Rate
from app.models import Rate, Port, BunkerRate
from app.models import Rate, Port, BunkerRate, DgCharge


def parse_date(s: str) -> date:
    y, m, d = s.split("-")
    return date(int(y), int(m), int(d))

def main() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        with open("data/ports.csv", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                db.add(Port(
                unlocode=r["unlocode"].strip().upper(),
                name=r["name"].strip(),
                country=(r.get("country") or "").strip().upper() or None,
                subdivision=(r.get("subdivision") or "").strip().upper() or None,
                ))
        db.commit()
        with open("data/bunker_rates.csv", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            bunker_count = 0
            for r in reader:
                db.add(BunkerRate(
                    trade=r["trade"].strip().upper(),
                    equipment_type=r["equipment_type"].strip().upper(),
                    currency=r["currency"].strip().upper(),
                    bunker_rate=Decimal(r["bunker_rate"]),
                    quarter_start=parse_date(r["quarter_start"]),
                    quarter_end=parse_date(r["quarter_end"]),
                ))
                bunker_count += 1
        db.commit()
        print(f"Seeded {bunker_count} bunker rates")

        with open("data/sample_rates.csv", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count = 0

            for r in reader:
                rate = Rate(
                    origin_unlocode=r["origin_unlocode"].strip().upper(),
                    destination_unlocode=r["destination_unlocode"].strip().upper(),
                    trade=r["trade"].strip().upper(),
                    equipment_type=r["equipment_type"].strip().upper(),
                    contract_type=r["contract_type"].strip().upper(),
                    service_level=r["service_level"].strip().upper(),
                    currency=r["currency"].strip().upper(),
                    base_rate=Decimal(r["base_rate"]),
                    effective_date=parse_date(r["effective_date"]),
                    expiry_date=parse_date(r["expiry_date"]),
                )
                db.add(rate)
                count += 1
        
        db.commit()
        print(f"Seeded {count} rates into rates.db")
        with open("data/dg_charges.csv", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            dg_count = 0
            for r in reader:
                db.add(DgCharge(
                    trade=r["trade"].strip().upper(),
                    equipment_type=r["equipment_type"].strip().upper(),
                    currency=r["currency"].strip().upper(),
                    dg_charge=Decimal(r["dg_charge"]),
                    quarter_start=parse_date(r["quarter_start"]),
                    quarter_end=parse_date(r["quarter_end"]),
                ))
                dg_count += 1
        db.commit()
        print(f"Seeded {dg_count} DG charges")

    finally:
        db.close()

if __name__ == "__main__":
    main()
