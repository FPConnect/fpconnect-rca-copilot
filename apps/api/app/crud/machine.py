"""CRUD operations for machines."""

from sqlalchemy.orm import Session

from app.models.machine import Machine


SEED_MACHINES = [
    {
        "code": "MRI-01",
        "name": "Ressonância Magnética 1.5T",
        "model": "Magnetom Aera",
        "location": "Radiologia",
        "type": "imaging",
        "status": "online",
        "criticality": "Alta",
        "last_failure": "Quench falso positivo no sistema de refrigeração",
        "recurrent_failures": 2,
    },
    {
        "code": "ECG-02",
        "name": "Monitor Multiparamétrico",
        "model": "IntelliVue MX450",
        "location": "UTI Adulto",
        "type": "monitoring",
        "status": "warning",
        "criticality": "Alta",
        "last_failure": "Perda intermitente de SpO2",
        "recurrent_failures": 4,
    },
    {
        "code": "VENT-03",
        "name": "Ventilador Pulmonar",
        "model": "Servo-u",
        "location": "UTI 2",
        "type": "life-support",
        "status": "online",
        "criticality": "Alta",
        "last_failure": "Alarme de pressão alta",
        "recurrent_failures": 1,
    },
    {
        "code": "DEF-04",
        "name": "Desfibrilador",
        "model": "HeartStart XL+",
        "location": "Pronto Atendimento",
        "type": "life-support",
        "status": "offline",
        "criticality": "Alta",
        "last_failure": "Falha no autoteste de bateria",
        "recurrent_failures": 3,
    },
    {
        "code": "INF-05",
        "name": "Bomba de Infusão",
        "model": "Volumat Agilia",
        "location": "Centro Cirúrgico",
        "type": "infusion",
        "status": "online",
        "criticality": "Média",
        "last_failure": "Oclusão recorrente em equipo",
        "recurrent_failures": 1,
    },
]


def ensure_seed_data(db: Session) -> None:
    if db.query(Machine).count() > 0:
        return
    db.add_all([Machine(**data) for data in SEED_MACHINES])
    db.commit()


def get_machines(db: Session):
    ensure_seed_data(db)
    return db.query(Machine).order_by(Machine.code.asc()).all()
