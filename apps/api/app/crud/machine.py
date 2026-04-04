"""CRUD operations for machines."""

from sqlalchemy.orm import Session

from app.models.machine import Machine


SEED_MACHINES = [
    {"code": "M001", "name": "MRI Scanner", "location": "Ward A", "type": "imaging", "status": "online"},
    {"code": "M002", "name": "ECG Monitor", "location": "ICU", "type": "monitoring", "status": "warning"},
    {"code": "M003", "name": "Ventilator", "location": "Ward B", "type": "life-support", "status": "online"},
    {"code": "M004", "name": "Defibrillator", "location": "Emergency", "type": "life-support", "status": "offline"},
]


def ensure_seed_data(db: Session) -> None:
    if db.query(Machine).count() > 0:
        return
    db.add_all([Machine(**data) for data in SEED_MACHINES])
    db.commit()


def get_machines(db: Session):
    ensure_seed_data(db)
    return db.query(Machine).order_by(Machine.code.asc()).all()
