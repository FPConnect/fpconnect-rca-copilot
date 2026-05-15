"""Seed clinical engineering demo data for FPConnect.

Run from apps/api:
    python scripts/seed_clinical.py
"""

from datetime import datetime, timedelta, timezone

from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models.machine import Machine
from app.models.playbook import Playbook, SLAContract
from app.models.ticket import Ticket, TicketLog
from app.models.user import User

UNITS = ["UTI Adulto", "Centro Cirúrgico", "Radiologia", "Pronto Atendimento", "Hemodinâmica"]

MACHINES = [
    ("MRI-01", "Ressonância Magnética 1.5T", "Magnetom Aera", "Radiologia", "imaging", "Alta", "online", 2),
    ("ECG-02", "Monitor Multiparamétrico", "IntelliVue MX450", "UTI Adulto", "monitoring", "Alta", "warning", 4),
    ("VENT-03", "Ventilador Pulmonar", "Servo-u", "UTI Adulto", "life-support", "Alta", "online", 1),
    ("DEF-04", "Desfibrilador", "HeartStart XL+", "Pronto Atendimento", "life-support", "Alta", "offline", 3),
    ("INF-05", "Bomba de Infusão", "Volumat Agilia", "Centro Cirúrgico", "infusion", "Média", "online", 1),
]

INCIDENTS = [
    ("ECG-02", "Perda intermitente de SpO2", "critical", "open", "Sensor com mau contato ou cabo danificado"),
    ("VENT-03", "Alarme de pressão alta durante ventilação", "critical", "in_progress", "Circuito obstruído ou filtro saturado"),
    ("DEF-04", "Falha no autoteste de bateria", "high", "open", "Bateria abaixo da capacidade mínima"),
    ("MRI-01", "Quench falso positivo no console", "high", "resolved", "Sensor de criogenia instável"),
    ("INF-05", "Oclusão recorrente em equipo", "medium", "open", "Equipo incompatível ou dobra na linha"),
    ("ECG-02", "Alarmes falsos de eletrodo solto", "medium", "resolved", "Eletrodo vencido ou preparo de pele inadequado"),
    ("VENT-03", "Falha de calibração do sensor de fluxo", "high", "in_progress", "Sensor contaminado após higienização"),
    ("MRI-01", "Atraso na inicialização da mesa", "medium", "open", "Atuador da mesa com lubrificação insuficiente"),
    ("DEF-04", "Pás não reconhecidas pelo equipamento", "critical", "open", "Conector de terapia oxidado"),
    ("INF-05", "Bolhas detectadas sem infusão", "low", "resolved", "Sensor óptico desalinhado"),
]

PLAYBOOKS = [
    ("Troca e validação de sensor SpO2", "Monitor Multiparamétrico", "1. Isolar leito.\n2. Trocar cabo/sensor.\n3. Validar curva e alarmes.\n4. Registrar evento."),
    ("Diagnóstico de circuito ventilatório obstruído", "Ventilador Pulmonar", "1. Verificar circuito.\n2. Inspecionar filtro HME.\n3. Rodar autoteste.\n4. Liberar com checklist."),
    ("Substituição de bateria do desfibrilador", "Desfibrilador", "1. Remover equipamento do uso.\n2. Trocar bateria.\n3. Executar autoteste.\n4. Registrar etiqueta de validade."),
]


def get_or_create_admin(db):
    user = db.query(User).filter(User.email == "admin@fpconnect.com").first()
    if user:
        return user
    user = User(
        email="admin@fpconnect.com",
        hashed_password=hash_password("admin123"),
        full_name="Engenharia Clínica",
        role="admin",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        user = get_or_create_admin(db)
        if db.query(Machine).count() == 0:
            for code, name, model, location, type_, criticality, status, recurrent in MACHINES:
                db.add(
                    Machine(
                        code=code,
                        name=name,
                        model=model,
                        location=location,
                        type=type_,
                        status=status,
                        criticality=criticality,
                        last_failure="Sem falha crítica nas últimas 24h" if status == "online" else "Falha pendente",
                        recurrent_failures=recurrent,
                    )
                )
            db.commit()

        if db.query(Ticket).count() == 0:
            now = datetime.now(timezone.utc)
            for index, (device_id, title, priority, status, cause) in enumerate(INCIDENTS):
                machine = db.query(Machine).filter(Machine.code == device_id).first()
                ticket = Ticket(
                    title=title,
                    description=f"Ocorrência registrada na unidade {machine.location if machine else UNITS[index % len(UNITS)]}.",
                    priority=priority,
                    status=status,
                    device_id=device_id,
                    location=machine.location if machine else UNITS[index % len(UNITS)],
                    creator_id=user.id,
                    root_cause=cause if status == "resolved" else None,
                    analysis_completed=now - timedelta(hours=index) if status == "resolved" else None,
                )
                db.add(ticket)
                db.flush()
                db.add_all(
                    [
                        TicketLog(ticket_id=ticket.id, user_id=user.id, action="abertura", detail="Incidente recebido pela engenharia clínica."),
                        TicketLog(ticket_id=ticket.id, user_id=user.id, action="triagem", detail="Severidade e unidade clínica validadas."),
                    ]
                )
            db.commit()

        if db.query(Playbook).count() == 0:
            db.add_all([Playbook(title=t, equipment=e, steps=s) for t, e, s in PLAYBOOKS])
            db.commit()

        if db.query(SLAContract).count() == 0:
            db.add_all(
                [
                    SLAContract(equipment="Ventilador Pulmonar", vendor="MedTech Care", response_time_hours=4, penalty="Crédito de 5% por violação", sla_compliance=97.5, expires_at=datetime.now(timezone.utc) + timedelta(days=20)),
                    SLAContract(equipment="Ressonância Magnética 1.5T", vendor="Imagem Prime", response_time_hours=8, penalty="Plantão técnico sem custo", sla_compliance=94.0, expires_at=datetime.now(timezone.utc) + timedelta(days=75)),
                ]
            )
            db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
    print("Clinical engineering seed data loaded.")
