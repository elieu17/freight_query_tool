from datetime import date
from sqlalchemy import text, bindparam
from sqlalchemy.orm import Session


def resolve_port_to_unlocodes(db: Session, raw: str, limit: int = 10) -> list[str]:
    s = (raw or "").strip()
    if not s:
        return []

    # If user selected something like "USNYC — New York..."
    if len(s) >= 5 and s[:5].isalnum():
        code = s[:5].upper()
        if len(code) == 5:
            return [code]

    sql = text("""
        SELECT unlocode
        FROM ports
        WHERE name LIKE :q
        ORDER BY name ASC
        LIMIT :limit
    """)
    rows = db.execute(sql, {"q": f"%{s}%", "limit": limit}).fetchall()
    return [r[0] for r in rows]


def search_rates(
    db: Session,
    origin: str,
    destination: str,
    equipment_type: str,
    ship_date: date,
    contract_type: str,
    dg: bool = False,
    limit: int = 50,
):
    origin_codes = resolve_port_to_unlocodes(db, origin)
    dest_codes = resolve_port_to_unlocodes(db, destination)

    if not origin_codes or not dest_codes:
        return []

    stmt = text("""
            SELECT
            r.id,
            r.origin_unlocode,
            op.name AS origin_name,
            r.destination_unlocode,
            dp.name AS destination_name,
            r.trade,
            r.equipment_type,
            r.contract_type,
            r.service_level,
            r.currency,
            r.base_rate,

            COALESCE(b.bunker_rate, 0) AS bunker_rate,

            CASE
                WHEN :dg = 1 THEN COALESCE(dg.dg_charge, 0)
                ELSE 0
            END AS dg_charge,

            (
                r.base_rate
                + COALESCE(b.bunker_rate, 0)
                + CASE WHEN :dg = 1 THEN COALESCE(dg.dg_charge, 0) ELSE 0 END
            ) AS all_in_ocean,

            r.effective_date,
            r.expiry_date
            FROM rates r
            LEFT JOIN ports op ON op.unlocode = r.origin_unlocode
            LEFT JOIN ports dp ON dp.unlocode = r.destination_unlocode

            LEFT JOIN bunker_rates b
            ON b.trade = r.trade
            AND b.equipment_type = r.equipment_type
            AND b.quarter_start <= date(:ship_date)
            AND b.quarter_end >= date(:ship_date)

            LEFT JOIN dg_charges dg
            ON dg.trade = r.trade
            AND dg.equipment_type = r.equipment_type
            AND dg.quarter_start <= date(:ship_date)
            AND dg.quarter_end >= date(:ship_date)

            WHERE r.origin_unlocode IN :origins
            AND r.destination_unlocode IN :destinations
            AND (:equipment_type IS NULL OR r.equipment_type = :equipment_type)
            AND r.effective_date <= date(:ship_date)
            AND r.expiry_date >= date(:ship_date)
            AND r.contract_type = :contract_type
            ORDER BY all_in_ocean ASC
            LIMIT :limit
        """).bindparams(
            bindparam("origins", expanding=True),
            bindparam("destinations", expanding=True),
        )


    params = {
        "origins": origin_codes,
        "destinations": dest_codes,
        "equipment_type": equipment_type.strip().upper() if equipment_type else None,
        "ship_date": ship_date.isoformat(),
        "contract_type": contract_type.strip().upper(),
        "limit": limit,
        "dg": 1 if dg else 0,
    }

    return db.execute(stmt, params).mappings().all()

def find_ports(db: Session, q: str, limit: int = 10):
    stmt = text("""
        SELECT unlocode, name, country, subdivision
        FROM ports
        WHERE unlocode LIKE :q_prefix
           OR name LIKE :q_like
        ORDER BY
          CASE WHEN unlocode LIKE :q_prefix THEN 0 ELSE 1 END,
          name ASC
        LIMIT :limit
    """)
    params = {
        "q_prefix": q.strip().upper() + "%",
        "q_like": "%" + q.strip() + "%",
        "limit": limit,
    }
    return db.execute(stmt, params).mappings().all()


