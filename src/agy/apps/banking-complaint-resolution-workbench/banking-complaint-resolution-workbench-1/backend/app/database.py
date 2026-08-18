import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, User, Complaint, AuditLog

SQLALCHEMY_DATABASE_URL = "sqlite:///./complaints.db"

# Create engine with connect_args for SQLite thread safety
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def calculate_sla(priority: str, base_time: datetime.datetime = None) -> datetime.datetime:
    """Calculate the SLA deadline based on priority."""
    if base_time is None:
        base_time = datetime.datetime.utcnow()
    
    if priority == "Critical":
        return base_time + datetime.timedelta(days=1)  # 24 Hours
    elif priority == "High":
        return base_time + datetime.timedelta(days=3)  # 3 Days
    elif priority == "Medium":
        return base_time + datetime.timedelta(days=7)  # 7 Days
    else:  # "Low"
        return base_time + datetime.timedelta(days=15)  # 15 Days

def init_db(database_url: str = SQLALCHEMY_DATABASE_URL) -> create_engine:
    """Initialize the database schema and populate it with robust mock data."""
    # Use the specified database url (allows test isolation)
    test_engine = create_engine(
        database_url, connect_args={"check_same_thread": False}
    )
    
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    Session = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = Session()
    
    try:
        # Check if users already exist, if so skip seeding
        if session.query(User).first() is not None:
            return test_engine
            
        # 1. Seed Users
        users = [
            User(username="jane_doe", name="Jane Doe", role="CSR"),
            User(username="john_smith", name="John Smith", role="Case Handler"),
            User(username="alice_johnson", name="Alice Johnson", role="Case Handler"),
            User(username="robert_vance", name="Robert Vance", role="Supervisor")
        ]
        for u in users:
            session.add(u)
        session.commit()
        
        # 2. Seed Complaints & matching Audit Logs
        now = datetime.datetime.utcnow()
        
        # Complaint 1: Registered card fee dispute
        c1 = Complaint(
            id="CRW-2026-0001",
            customer_name="Marcus Aurelius",
            account_number="ACT-98234-92",
            customer_email="marcus@meditations.com",
            customer_phone="+1-555-0192",
            title="Overcharged Credit Card Annual Fee",
            description="The customer claims they were verbally promised a waiver of the $150 annual fee for their Gold Card during a promotion. The fee was posted on August 1st.",
            category="Credit Cards",
            subcategory="Fee Dispute",
            disputed_amount=150.0,
            priority="Medium",
            status="Registered",
            sla_deadline=calculate_sla("Medium", now),
            logged_by="jane_doe"
        )
        session.add(c1)
        session.commit()
        
        log1 = AuditLog(
            complaint_id="CRW-2026-0001",
            timestamp=now - datetime.timedelta(hours=2),
            user_name="Jane Doe",
            user_role="CSR",
            event_type="Log Complaint",
            description="Logged complaint regarding unauthorized Credit Card Annual fee of $150.00."
        )
        session.add(log1)
        
        # Complaint 2: Unauthorized transaction
        c2 = Complaint(
            id="CRW-2026-0002",
            customer_name="Cleopatra Selene",
            account_number="ACT-10023-88",
            customer_email="cleo@egypt.gov",
            customer_phone="+1-555-1010",
            title="Unauthorized Debit Card Discrepancy",
            description="Customer spotted an unauthorized transaction of $350.00 from a gas station in another state while they were in possession of their physical card. Needs urgent card freeze and investigation.",
            category="Digital Banking",
            subcategory="Unauthorised Charge",
            disputed_amount=350.0,
            priority="Critical",
            status="Under Investigation",
            sla_deadline=calculate_sla("Critical", now),
            assigned_to="john_smith",
            logged_by="jane_doe"
        )
        session.add(c2)
        session.commit()
        
        log2_1 = AuditLog(
            complaint_id="CRW-2026-0002",
            timestamp=now - datetime.timedelta(hours=4),
            user_name="Jane Doe",
            user_role="CSR",
            event_type="Log Complaint",
            description="Logged critical complaint for unauthorized charge of $350.00. Priority set to Critical."
        )
        log2_2 = AuditLog(
            complaint_id="CRW-2026-0002",
            timestamp=now - datetime.timedelta(hours=3),
            user_name="John Smith",
            user_role="Case Handler",
            event_type="Claim Case",
            description="Claimed case from the queue and started investigation. Initiated card freeze request."
        )
        session.add_all([log2_1, log2_2])
        
        # Complaint 3: Mortgage delay pending approval
        c3 = Complaint(
            id="CRW-2026-0003",
            customer_name="Alexander G. Bell",
            account_number="ACT-44561-12",
            customer_email="alex@telephone.org",
            customer_phone="+1-555-1876",
            title="Severe Mortgage Document Processing Delay",
            description="Customer submitted all requested mortgage documentation 2 weeks ago. Closing date is approaching in 5 days, and mortgage officers are not responding. Customer is extremely anxious.",
            category="Mortgages",
            subcategory="Service Delay",
            disputed_amount=0.0,
            priority="High",
            status="Resolution Proposed",
            sla_deadline=calculate_sla("High", now),
            assigned_to="alice_johnson",
            logged_by="jane_doe",
            resolution_notes="Contacted the mortgage underwriting team directly and expedited the file. Approved underwriting. Proposing $100.00 customer goodwill refund for processing delay stress and delay."
        )
        session.add(c3)
        session.commit()
        
        log3_1 = AuditLog(
            complaint_id="CRW-2026-0003",
            timestamp=now - datetime.timedelta(days=2),
            user_name="Jane Doe",
            user_role="CSR",
            event_type="Log Complaint",
            description="Logged High priority complaint regarding mortgage paperwork delay."
        )
        log3_2 = AuditLog(
            complaint_id="CRW-2026-0003",
            timestamp=now - datetime.timedelta(days=1, hours=6),
            user_name="Alice Johnson",
            user_role="Case Handler",
            event_type="Claim Case",
            description="Claimed case and initiated fast-track underwriting contact."
        )
        log3_3 = AuditLog(
            complaint_id="CRW-2026-0003",
            timestamp=now - datetime.timedelta(hours=1),
            user_name="Alice Johnson",
            user_role="Case Handler",
            event_type="Submit Proposal",
            description="Underwriting approved. Submitted resolution proposal: Goodwill refund of $100.00 and written apology."
        )
        session.add_all([log3_1, log3_2, log3_3])
        
        # Complaint 4: Resolved savings rate dispute
        c4 = Complaint(
            id="CRW-2026-0004",
            customer_name="Isaac Newton",
            account_number="ACT-88771-00",
            customer_email="isaac@principia.edu",
            customer_phone="+1-555-1687",
            title="Savings Account Promo Interest Rate Discrepancy",
            description="Customer states their High-Yield Savings Account was opened under a 4.5% promo rate, but interest is only posting at the base rate of 2.0%.",
            category="Savings Accounts",
            subcategory="Interest Dispute",
            disputed_amount=75.45,
            priority="Low",
            status="Resolved",
            sla_deadline=calculate_sla("Low", now),
            assigned_to="john_smith",
            logged_by="jane_doe",
            resolution_notes="Discovered promo rate was pending a minimum balance of $10,000, which was met on day 5 of opening. Manually calculated the difference of $75.45 and applied it to the savings account. Customer is satisfied with the speed and resolution."
        )
        session.add(c4)
        session.commit()
        
        log4_1 = AuditLog(
            complaint_id="CRW-2026-0004",
            timestamp=now - datetime.timedelta(days=10),
            user_name="Jane Doe",
            user_role="CSR",
            event_type="Log Complaint",
            description="Logged Savings Account promo interest dispute."
        )
        log4_2 = AuditLog(
            complaint_id="CRW-2026-0004",
            timestamp=now - datetime.timedelta(days=9),
            user_name="John Smith",
            user_role="Case Handler",
            event_type="Claim Case",
            description="Claimed case and began interest rate calculations review."
        )
        log4_3 = AuditLog(
            complaint_id="CRW-2026-0004",
            timestamp=now - datetime.timedelta(days=8),
            user_name="John Smith",
            user_role="Case Handler",
            event_type="Submit Proposal",
            description="Proposed manual correction of $75.45 to account."
        )
        log4_4 = AuditLog(
            complaint_id="CRW-2026-0004",
            timestamp=now - datetime.timedelta(days=7),
            user_name="Robert Vance",
            user_role="Supervisor",
            event_type="Approve Case",
            description="Approved proposal and credited $75.45 to savings account. Status changed to Resolved."
        )
        session.add_all([log4_1, log4_2, log4_3, log4_4])
        session.commit()
        
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
        
    return test_engine
