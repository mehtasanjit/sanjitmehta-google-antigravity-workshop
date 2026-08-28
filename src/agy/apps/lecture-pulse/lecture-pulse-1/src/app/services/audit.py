from app.models import AuditLog


def write_audit(db, actor_subject: str, actor_role: str, action: str, target_type: str, target_id=None):
    db.add(AuditLog(
        actor_subject=actor_subject,
        actor_role=actor_role,
        action=action,
        target_type=target_type,
        target_id=target_id
    ))
