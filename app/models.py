from sqlalchemy import Column, Integer, String, Date, Numeric, Index
from app.db import Base

class Rate(Base):
    __tablename__ = "rates"

    id = Column(Integer, primary_key=True)
    origin_unlocode = Column(String, nullable=False)
    destination_unlocode = Column(String, nullable=False)
    trade = Column(String, nullable=False)

    equipment_type = Column(String, nullable=False)
    contract_type = Column(String, nullable=False)  # <-- NEW

    service_level = Column(String, nullable=False)
    currency = Column(String, nullable=False)
    base_rate = Column(Numeric(12, 2), nullable=False)

    effective_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=False)




class Port(Base):
    __tablename__ = "ports"

    unlocode = Column(String, primary_key=True)   # e.g., "USNYC"
    name = Column(String, nullable=False)         # e.g., "New York"
    country = Column(String, nullable=True)       # e.g., "US"
    subdivision = Column(String, nullable=True)   # e.g., "NY"

class BunkerRate(Base):
    __tablename__ = "bunker_rates"

    id = Column(Integer, primary_key=True)
    trade = Column(String, nullable=False)             # e.g., "TPEB"
    equipment_type = Column(String, nullable=False)    # e.g., "40HC"
    currency = Column(String, nullable=False)          # e.g., "USD"
    bunker_rate = Column(Numeric(12, 2), nullable=False)

    quarter_start = Column(Date, nullable=False)       # e.g., 2026-01-01
    quarter_end = Column(Date, nullable=False)         # e.g., 2026-03-31

class DgCharge(Base):
    __tablename__ = "dg_charges"

    id = Column(Integer, primary_key=True)
    trade = Column(String, nullable=False)             # e.g., "TPEB"
    equipment_type = Column(String, nullable=False)    # e.g., "40HC"
    currency = Column(String, nullable=False)          # e.g., "USD"
    dg_charge = Column(Numeric(12, 2), nullable=False)

    quarter_start = Column(Date, nullable=False)
    quarter_end = Column(Date, nullable=False)

Index("ix_dg_trade_eq", DgCharge.trade, DgCharge.equipment_type)
Index("ix_dg_quarter", DgCharge.quarter_start, DgCharge.quarter_end)
Index("ix_bunker_trade_eq", BunkerRate.trade, BunkerRate.equipment_type)
Index("ix_bunker_quarter", BunkerRate.quarter_start, BunkerRate.quarter_end)
Index("ix_rates_lane", Rate.origin_unlocode, Rate.destination_unlocode, Rate.equipment_type)
Index("ix_rates_validity", Rate.effective_date, Rate.expiry_date)
Index("ix_rates_contract_type", Rate.contract_type)
Index("ix_ports_name", Port.name)
Index("ix_ports_country", Port.country)
