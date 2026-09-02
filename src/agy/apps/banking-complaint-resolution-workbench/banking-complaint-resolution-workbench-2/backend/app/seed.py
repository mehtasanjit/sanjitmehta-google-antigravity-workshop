import datetime
import json
from sqlalchemy.orm import Session
from .database import Base, engine
from . import models

def seed_db(db: Session):
    # Reset database
    current_engine = db.bind if db.bind is not None else engine
    Base.metadata.drop_all(bind=current_engine)
    Base.metadata.create_all(bind=current_engine)
    db.expunge_all()

    now = datetime.datetime.utcnow()

    # Define synthetic complaints data
    complaints_data = [
        # 1. RESOLVED
        {
            "reference_number": "CMP-2026-001",
            "customer_name": "Eleanor Vance",
            "customer_id": "CUST-98210",
            "customer_email": "eleanor.vance@example.com",
            "customer_phone": "555-0192",
            "account_number": "ACT-100293",
            "account_type": "Checking",
            "product_type": "checking",
            "category": "Overdraft Fees",
            "priority": "LOW",
            "channel": "Online",
            "subject": "Overdraft Fee Disputed",
            "narrative": "I was charged an overdraft fee of $35 even though my direct deposit was initiated before the transaction. This is unfair as the funds should have been available.",
            "disputed_amount": 35.0,
            "status": "RESOLVED",
            "assigned_to": "Jane Doe",
            "root_cause": "System timing lag in deposit clearing vs debit posting.",
            "investigation_notes": "Reviewed ledger timestamps. Direct deposit settled at 6:01 AM while card transaction posted at 6:05 AM, but standard batch processing registered them in reverse order. Valid dispute.",
            "refund_amount": 35.0,
            "goodwill_amount": 10.0,
            "interest_amount": 1.50,
            "total_redress": 46.50,
            "review_decision": "APPROVED",
            "supervisor_name": "Sarah Jenkins",
            "supervisor_notes": "Valid systemic timing issue. Recommended refund approved.",
            "sla_target_hours": 168,
            "days_ago_created": 15,
            "days_ago_resolved": 10,
            "audit_trail": [
                {"action": "CREATED", "role": "Customer", "name": "Eleanor Vance", "details": "Complaint submitted through web portal.", "offset_days": 15},
                {"action": "ASSIGNED", "role": "Case Handler", "name": "Jane Doe", "details": "Assigned to Jane Doe for investigation.", "offset_days": 14},
                {"action": "INVESTIGATION_UPDATED", "role": "Case Handler", "name": "Jane Doe", "details": "Completed ledger review. Confirmed systemic timing lag of deposit clearing.", "offset_days": 13},
                {"action": "REDRESS_CALCULATED", "role": "Case Handler", "name": "Jane Doe", "details": "Calculated total redress: $35.00 refund, $10.00 goodwill, $1.50 interest.", "offset_days": 12, "metadata": {"refund": 35.0, "goodwill": 10.0, "interest": 1.5}},
                {"action": "SUBMITTED_FOR_REVIEW", "role": "Case Handler", "name": "Jane Doe", "details": "Submitted to Sarah Jenkins for approval.", "offset_days": 12},
                {"action": "SUPERVISOR_APPROVED", "role": "Supervisor", "name": "Sarah Jenkins", "details": "Approved redress of $46.50. Closing case.", "offset_days": 11},
                {"action": "RESOLVED", "role": "Case Handler", "name": "Jane Doe", "details": "Complaint fully resolved. Funds credited back to account ACT-100293.", "offset_days": 10}
            ]
        },
        # 2. NEW
        {
            "reference_number": "CMP-2026-002",
            "customer_name": "Arthur Dent",
            "customer_id": "CUST-42420",
            "customer_email": "arthur.dent@example.com",
            "customer_phone": "555-4242",
            "account_number": "ACT-888999",
            "account_type": "Credit Card",
            "product_type": "credit cards",
            "category": "Unauthorized Charges",
            "priority": "CRITICAL",
            "channel": "Phone",
            "subject": "Fraudulent charges from overseas",
            "narrative": "I noticed three unauthorized charges from a vendor in London on my credit card statement totaling $1,450. I have not been to London recently and my card is in my possession.",
            "disputed_amount": 1450.0,
            "status": "NEW",
            "assigned_to": None,
            "root_cause": None,
            "investigation_notes": None,
            "refund_amount": 0.0,
            "goodwill_amount": 0.0,
            "interest_amount": 0.0,
            "total_redress": 0.0,
            "review_decision": "NONE",
            "supervisor_name": None,
            "supervisor_notes": None,
            "sla_target_hours": 48,
            "days_ago_created": 1,
            "days_ago_resolved": None,
            "audit_trail": [
                {"action": "CREATED", "role": "Customer Support Representative", "name": "Kevin Shields", "details": "Complaint initiated over phone intake due to suspect overseas transactions.", "offset_days": 1}
            ]
        },
        # 3. IN_INVESTIGATION
        {
            "reference_number": "CMP-2026-003",
            "customer_name": "Marcus Aurelius",
            "customer_id": "CUST-00121",
            "customer_email": "marcus.aurelius@example.com",
            "customer_phone": "555-1900",
            "account_number": "ACT-304050",
            "account_type": "Mortgage",
            "product_type": "mortgages",
            "category": "Escrow Dispute",
            "priority": "HIGH",
            "channel": "Mail",
            "subject": "Escrow account balance calculation error",
            "narrative": "My annual escrow analysis claims my monthly payment must increase by $320 due to a shortage. I calculated my tax and insurance myself, and it should only be a $50 increase. I believe you over-estimated the property tax.",
            "disputed_amount": 3840.0,
            "status": "IN_INVESTIGATION",
            "assigned_to": "John Smith",
            "root_cause": None,
            "investigation_notes": "Analyzing the local county tax assessor appraisal data. There is a discrepancy between county tax records and our automated mortgage servicer records.",
            "refund_amount": 0.0,
            "goodwill_amount": 0.0,
            "interest_amount": 0.0,
            "total_redress": 0.0,
            "review_decision": "NONE",
            "supervisor_name": None,
            "supervisor_notes": None,
            "sla_target_hours": 120,
            "days_ago_created": 8,
            "days_ago_resolved": None,
            "audit_trail": [
                {"action": "CREATED", "role": "Customer", "name": "Marcus Aurelius", "details": "Complaint received via postal mail and scanned.", "offset_days": 8},
                {"action": "ASSIGNED", "role": "Case Handler", "name": "John Smith", "details": "Assigned to John Smith for escrow re-appraisal review.", "offset_days": 7},
                {"action": "INVESTIGATION_UPDATED", "role": "Case Handler", "name": "John Smith", "details": "Contacted county tax office. Waiting for certified property tax statement.", "offset_days": 5}
            ]
        },
        # 4. UNDER_REVIEW
        {
            "reference_number": "CMP-2026-004",
            "customer_name": "Diana Prince",
            "customer_id": "CUST-19410",
            "customer_email": "diana.prince@example.com",
            "customer_phone": "555-7584",
            "account_number": "ACT-555111",
            "account_type": "Personal Loan",
            "product_type": "personal loans",
            "category": "Payment Allocation",
            "priority": "MEDIUM",
            "channel": "Online",
            "subject": "Extra payment applied as regular interest rather than principal",
            "narrative": "I paid an extra $500 on my loan with explicit instructions to apply it directly to the principal balance. Instead, the payment was split as a pre-payment for next month's principal and interest.",
            "disputed_amount": 500.0,
            "status": "UNDER_REVIEW",
            "assigned_to": "Alice Johnson",
            "root_cause": "Automatic billing system default allocation rules overrode customer instructions.",
            "investigation_notes": "Confirmed customer checked 'Apply to Principal Only' on the digital transfer interface, but system logic allocated it as regular monthly payments due to a batch job overlap.",
            "refund_amount": 0.0,
            "goodwill_amount": 50.0,
            "interest_amount": 12.40,
            "total_redress": 62.40,
            "review_decision": "NONE",
            "supervisor_name": None,
            "supervisor_notes": None,
            "sla_target_hours": 96,
            "days_ago_created": 6,
            "days_ago_resolved": None,
            "audit_trail": [
                {"action": "CREATED", "role": "Customer", "name": "Diana Prince", "details": "Intake via digital form.", "offset_days": 6},
                {"action": "ASSIGNED", "role": "Case Handler", "name": "Alice Johnson", "details": "Assigned to Alice Johnson.", "offset_days": 5},
                {"action": "INVESTIGATION_UPDATED", "role": "Case Handler", "name": "Alice Johnson", "details": "Audit of ledger complete. System failed to capture principal-only flag.", "offset_days": 4},
                {"action": "REDRESS_CALCULATED", "role": "Case Handler", "name": "Alice Johnson", "details": "Corrected allocation. Waiving $12.40 in miscalculated interest, offering $50.00 goodwill payment.", "offset_days": 3, "metadata": {"refund": 0.0, "goodwill": 50.0, "interest": 12.4}},
                {"action": "STATUS_CHANGED", "role": "Case Handler", "name": "Alice Johnson", "details": "Submitting for approval.", "from_status": "IN_INVESTIGATION", "to_status": "UNDER_REVIEW", "offset_days": 3}
            ]
        },
        # 5. APPROVED
        {
            "reference_number": "CMP-2026-005",
            "customer_name": "Sherlock Holmes",
            "customer_id": "CUST-22100",
            "customer_email": "sherlock@example.com",
            "customer_phone": "555-221B",
            "account_number": "ACT-999333",
            "account_type": "Checking",
            "product_type": "wire transfers",
            "category": "Delayed Wire Transfer",
            "priority": "HIGH",
            "channel": "Phone",
            "subject": "Delayed international wire transfer fee",
            "narrative": "My outgoing wire transfer of $5,000 to Switzerland took 7 business days instead of the promised 24 hours. The recipient charged me a late fee, and I demand a refund of the wire transfer fee.",
            "disputed_amount": 45.0,
            "status": "APPROVED",
            "assigned_to": "Bob Wilson",
            "root_cause": "Intermediate correspondent bank held funds for manual review.",
            "investigation_notes": "We sent the wire within 2 hours. However, the Swiss intermediary bank flagged the transaction for manual review due to a name similarity block. We are refunding our $45 wire fee and $50 of the late fee as a goodwill gesture.",
            "refund_amount": 45.0,
            "goodwill_amount": 50.0,
            "interest_amount": 0.0,
            "total_redress": 95.0,
            "review_decision": "APPROVED",
            "supervisor_name": "Sarah Jenkins",
            "supervisor_notes": "Bob handled this nicely. Wire fee and late fee reimbursement approved.",
            "sla_target_hours": 72,
            "days_ago_created": 4,
            "days_ago_resolved": None,
            "audit_trail": [
                {"action": "CREATED", "role": "Customer", "name": "Sherlock Holmes", "details": "Phone intake created.", "offset_days": 4},
                {"action": "ASSIGNED", "role": "Case Handler", "name": "Bob Wilson", "details": "Assigned to Bob Wilson.", "offset_days": 4},
                {"action": "INVESTIGATION_UPDATED", "role": "Case Handler", "name": "Bob Wilson", "details": "Traced Swift message trail. Cleared our bank's gateway instantly.", "offset_days": 3},
                {"action": "REDRESS_CALCULATED", "role": "Case Handler", "name": "Bob Wilson", "details": "Refund wire fee $45, goodwill compensation $50.", "offset_days": 2, "metadata": {"refund": 45.0, "goodwill": 50.0, "interest": 0.0}},
                {"action": "STATUS_CHANGED", "role": "Case Handler", "name": "Bob Wilson", "details": "Submitting to supervisor.", "from_status": "IN_INVESTIGATION", "to_status": "UNDER_REVIEW", "offset_days": 2},
                {"action": "SUPERVISOR_APPROVED", "role": "Supervisor", "name": "Sarah Jenkins", "details": "Approved. Initiating settlement transfer.", "offset_days": 1}
            ]
        },
        # 6. ESCALATED
        {
            "reference_number": "CMP-2026-006",
            "customer_name": "Luke Skywalker",
            "customer_id": "CUST-00001",
            "customer_email": "luke@example.com",
            "customer_phone": "555-1111",
            "account_number": "ACT-121212",
            "account_type": "Checking",
            "product_type": "fraud claims",
            "category": "ATM Fraud Dispute",
            "priority": "CRITICAL",
            "channel": "Branch",
            "subject": "ATM withdrawal dispute - Card skimming suspected",
            "narrative": "Someone withdrew $800 from my checking account at a convenience store ATM in another city. I have my physical card with me and never gave my PIN to anyone.",
            "disputed_amount": 800.0,
            "status": "ESCALATED",
            "assigned_to": "Charlie Brown",
            "root_cause": None,
            "investigation_notes": "We inspected the security footage of the store ATM. The perpetrator used a cloned magstripe card. However, because our cards use EMV chips, we need to investigate how the fallback transactions were approved.",
            "refund_amount": 0.0,
            "goodwill_amount": 0.0,
            "interest_amount": 0.0,
            "total_redress": 0.0,
            "review_decision": "NONE",
            "supervisor_name": None,
            "supervisor_notes": None,
            "sla_target_hours": 48,
            "days_ago_created": 3,
            "days_ago_resolved": None,
            "audit_trail": [
                {"action": "CREATED", "role": "Customer", "name": "Luke Skywalker", "details": "In-branch complaint form received.", "offset_days": 3},
                {"action": "ASSIGNED", "role": "Case Handler", "name": "Charlie Brown", "details": "Assigned to Fraud Specialist Charlie Brown.", "offset_days": 3},
                {"action": "INVESTIGATION_UPDATED", "role": "Case Handler", "name": "Charlie Brown", "details": "Secured convenience store CCTV files.", "offset_days": 2},
                {"action": "ESCALATED", "role": "Case Handler", "name": "Charlie Brown", "details": "Escalated to High-Tier Cybersecurity and Card Security Team due to magstripe fallback exploit.", "offset_days": 1}
            ]
        },
        # 7. NEW
        {
            "reference_number": "CMP-2026-007",
            "customer_name": "Frodo Baggins",
            "customer_id": "CUST-00009",
            "customer_email": "frodo.baggins@example.com",
            "customer_phone": "555-1600",
            "account_number": "ACT-555555",
            "account_type": "Checking",
            "product_type": "checking",
            "category": "Double Charge",
            "priority": "MEDIUM",
            "channel": "Online",
            "subject": "Double charged at local tavern",
            "narrative": "I visited a merchant yesterday and my transaction was declined the first time. I swiped again and it went through. Today I see two pending charges of $120.00 each. Please reverse one.",
            "disputed_amount": 120.0,
            "status": "NEW",
            "assigned_to": None,
            "root_cause": None,
            "investigation_notes": None,
            "refund_amount": 0.0,
            "goodwill_amount": 0.0,
            "interest_amount": 0.0,
            "total_redress": 0.0,
            "review_decision": "NONE",
            "supervisor_name": None,
            "supervisor_notes": None,
            "sla_target_hours": 72,
            "days_ago_created": 2,
            "days_ago_resolved": None,
            "audit_trail": [
                {"action": "CREATED", "role": "Customer", "name": "Frodo Baggins", "details": "Digital intake initiated.", "offset_days": 2}
            ]
        },
        # 8. IN_INVESTIGATION
        {
            "reference_number": "CMP-2026-008",
            "customer_name": "Tony Stark",
            "customer_id": "CUST-03000",
            "customer_email": "tony@example.com",
            "customer_phone": "555-3000",
            "account_number": "ACT-300000",
            "account_type": "Credit Card",
            "product_type": "credit cards",
            "category": "Interest APR Dispute",
            "priority": "MEDIUM",
            "channel": "Online",
            "subject": "Promotional 0% APR not applied to purchase",
            "narrative": "I opened a card under a 0% introductory APR for 12 months. However, my statement shows $150.00 of interest charges for my purchase of high-grade copper wire. Please fix this.",
            "disputed_amount": 150.0,
            "status": "IN_INVESTIGATION",
            "assigned_to": "Jane Doe",
            "root_cause": None,
            "investigation_notes": "Checking if promotional code 'STARK0' was entered on the application form. System history shows promo application flag is false, but promo advertisements were active.",
            "refund_amount": 0.0,
            "goodwill_amount": 0.0,
            "interest_amount": 0.0,
            "total_redress": 0.0,
            "review_decision": "NONE",
            "supervisor_name": None,
            "supervisor_notes": None,
            "sla_target_hours": 120,
            "days_ago_created": 5,
            "days_ago_resolved": None,
            "audit_trail": [
                {"action": "CREATED", "role": "Customer", "name": "Tony Stark", "details": "Online complaint registered.", "offset_days": 5},
                {"action": "ASSIGNED", "role": "Case Handler", "name": "Jane Doe", "details": "Assigned to Jane Doe for promotion validity checks.", "offset_days": 4},
                {"action": "INVESTIGATION_UPDATED", "role": "Case Handler", "name": "Jane Doe", "details": "Requested promotional code audit from marketing team.", "offset_days": 2}
            ]
        },
        # 9. RESOLVED
        {
            "reference_number": "CMP-2026-009",
            "customer_name": "Winston Smith",
            "customer_id": "CUST-19840",
            "customer_email": "winston.smith@example.com",
            "customer_phone": "555-1984",
            "account_number": "ACT-848484",
            "account_type": "Mortgage",
            "product_type": "mortgages",
            "category": "Prepayment Penalty",
            "priority": "HIGH",
            "channel": "Mail",
            "subject": "Disputed Prepayment Penalty Fee",
            "narrative": "I made an early payment to pay off my mortgage completely, and was hit with a $1,200 prepayment penalty. The disclosure forms were extremely misleading, and did not state this would apply in my state.",
            "disputed_amount": 1200.0,
            "status": "RESOLVED",
            "assigned_to": "John Smith",
            "root_cause": "Disclosure template error. Selected state regulations were not printed.",
            "investigation_notes": "Verified that disclosure forms printed in Q3 2025 omitted the state-specific rider regarding prepayment terms. Customer did not receive proper notice, hence penalty is unenforceable.",
            "refund_amount": 1200.0,
            "goodwill_amount": 100.0,
            "interest_amount": 15.0,
            "total_redress": 1315.0,
            "review_decision": "APPROVED",
            "supervisor_name": "Sarah Jenkins",
            "supervisor_notes": "Good legal catch John. Omitting state regulations forces us to waive the fee. Refund approved.",
            "sla_target_hours": 240,
            "days_ago_created": 20,
            "days_ago_resolved": 15,
            "audit_trail": [
                {"action": "CREATED", "role": "Customer", "name": "Winston Smith", "details": "Letter received and ingested.", "offset_days": 20},
                {"action": "ASSIGNED", "role": "Case Handler", "name": "John Smith", "details": "Assigned to John Smith.", "offset_days": 19},
                {"action": "INVESTIGATION_UPDATED", "role": "Case Handler", "name": "John Smith", "details": "Confirmed physical disclosure documents of state were missing the rider.", "offset_days": 18},
                {"action": "REDRESS_CALCULATED", "role": "Case Handler", "name": "John Smith", "details": "Waiving full $1,200 fee, plus $100 goodwill, and $15 accrued interest.", "offset_days": 17, "metadata": {"refund": 1200.0, "goodwill": 100.0, "interest": 15.0}},
                {"action": "STATUS_CHANGED", "role": "Case Handler", "name": "John Smith", "details": "Submitting for review.", "from_status": "IN_INVESTIGATION", "to_status": "UNDER_REVIEW", "offset_days": 17},
                {"action": "SUPERVISOR_APPROVED", "role": "Supervisor", "name": "Sarah Jenkins", "details": "Approved. Prepayment penalty waived completely.", "offset_days": 16},
                {"action": "RESOLVED", "role": "Case Handler", "name": "John Smith", "details": "Ledger corrected. Customer notified of resolution.", "offset_days": 15}
            ]
        },
        # 10. UNDER_REVIEW
        {
            "reference_number": "CMP-2026-010",
            "customer_name": "Clara Oswald",
            "customer_id": "CUST-11111",
            "customer_email": "clara.oswald@example.com",
            "customer_phone": "555-1100",
            "account_number": "ACT-444888",
            "account_type": "Personal Loan",
            "product_type": "personal loans",
            "category": "Billing Discrepancy",
            "priority": "LOW",
            "channel": "Phone",
            "subject": "Incorrect monthly billing statement amount",
            "narrative": "My loan agreement specifies a fixed payment of $250.00/month. The latest bill claims I owe $285.00. I paid $250 but am now being marked as short and charged late fees.",
            "disputed_amount": 35.0,
            "status": "UNDER_REVIEW",
            "assigned_to": "Alice Johnson",
            "root_cause": "Double administrative fee calculation error.",
            "investigation_notes": "We found a double charging of the account administration fee. Reversing the $35.00 difference and erasing the late record.",
            "refund_amount": 35.0,
            "goodwill_amount": 15.0,
            "interest_amount": 0.0,
            "total_redress": 50.0,
            "review_decision": "NONE",
            "supervisor_name": None,
            "supervisor_notes": None,
            "sla_target_hours": 168,
            "days_ago_created": 4,
            "days_ago_resolved": None,
            "audit_trail": [
                {"action": "CREATED", "role": "Customer Support Representative", "name": "Kevin Shields", "details": "Phone complaint created.", "offset_days": 4},
                {"action": "ASSIGNED", "role": "Case Handler", "name": "Alice Johnson", "details": "Assigned to Alice Johnson.", "offset_days": 4},
                {"action": "INVESTIGATION_UPDATED", "role": "Case Handler", "name": "Alice Johnson", "details": "Identified the double billing of admin fee in database table.", "offset_days": 3},
                {"action": "REDRESS_CALCULATED", "role": "Case Handler", "name": "Alice Johnson", "details": "Calculated $35 refund and $15 goodwill.", "offset_days": 2, "metadata": {"refund": 35.0, "goodwill": 15.0, "interest": 0.0}},
                {"action": "STATUS_CHANGED", "role": "Case Handler", "name": "Alice Johnson", "details": "Submitted for approval.", "from_status": "IN_INVESTIGATION", "to_status": "UNDER_REVIEW", "offset_days": 2}
            ]
        },
        # 11. NEW
        {
            "reference_number": "CMP-2026-011",
            "customer_name": "Frodo Baggins",
            "customer_id": "CUST-00009",
            "customer_email": "frodo.baggins@example.com",
            "customer_phone": "555-1600",
            "account_number": "ACT-555555",
            "account_type": "Checking",
            "product_type": "wire transfers",
            "category": "Exchange Rate Dispute",
            "priority": "MEDIUM",
            "channel": "Online",
            "subject": "Disputed currency conversion fee rate",
            "narrative": "I transferred money to Rivendell and the exchange rate used was 3% higher than what was shown in the app right before I tapped confirm. I was overcharged by $75 equivalent.",
            "disputed_amount": 75.0,
            "status": "NEW",
            "assigned_to": None,
            "root_cause": None,
            "investigation_notes": None,
            "refund_amount": 0.0,
            "goodwill_amount": 0.0,
            "interest_amount": 0.0,
            "total_redress": 0.0,
            "review_decision": "NONE",
            "supervisor_name": None,
            "supervisor_notes": None,
            "sla_target_hours": 120,
            "days_ago_created": 1,
            "days_ago_resolved": None,
            "audit_trail": [
                {"action": "CREATED", "role": "Customer", "name": "Frodo Baggins", "details": "Online application logged.", "offset_days": 1}
            ]
        },
        # 12. IN_INVESTIGATION
        {
            "reference_number": "CMP-2026-012",
            "customer_name": "Peter Parker",
            "customer_id": "CUST-00700",
            "customer_email": "peter.parker@example.com",
            "customer_phone": "555-0900",
            "account_number": "ACT-777111",
            "account_type": "Checking",
            "product_type": "fraud claims",
            "category": "Phishing Scam Claim",
            "priority": "CRITICAL",
            "channel": "Online",
            "subject": "Phishing website cloned bank login page",
            "narrative": "I received an SMS claiming to be from the fraud division and clicked on the link. I logged in and $500 was immediately moved from my checking account via Zelle to an unknown address.",
            "disputed_amount": 500.0,
            "status": "IN_INVESTIGATION",
            "assigned_to": "Bob Wilson",
            "root_cause": None,
            "investigation_notes": "The transfer was executed using Zelle. We are checking if we can request a recall of the transfer from the receiving institution.",
            "refund_amount": 0.0,
            "goodwill_amount": 0.0,
            "interest_amount": 0.0,
            "total_redress": 0.0,
            "review_decision": "NONE",
            "supervisor_name": None,
            "supervisor_notes": None,
            "sla_target_hours": 48,
            "days_ago_created": 3,
            "days_ago_resolved": None,
            "audit_trail": [
                {"action": "CREATED", "role": "Customer", "name": "Peter Parker", "details": "Online scam portal report submitted.", "offset_days": 3},
                {"action": "ASSIGNED", "role": "Case Handler", "name": "Bob Wilson", "details": "Assigned to Bob Wilson.", "offset_days": 3},
                {"action": "INVESTIGATION_UPDATED", "role": "Case Handler", "name": "Bob Wilson", "details": "Submitted standard Zelle dispute payload to receiving bank.", "offset_days": 1}
            ]
        },
        # 13. RESOLVED
        {
            "reference_number": "CMP-2026-013",
            "customer_name": "Bilbo Baggins",
            "customer_id": "CUST-00111",
            "customer_email": "bilbo@example.com",
            "customer_phone": "555-1111",
            "account_number": "ACT-111111",
            "account_type": "Checking",
            "product_type": "checking",
            "category": "Monthly Service Fee Dispute",
            "priority": "LOW",
            "channel": "Phone",
            "subject": "Senior citizen account monthly fee waiver",
            "narrative": "I am well over 111 years old. My account was supposed to be converted to a Senior Waiver checking account. Instead I was charged a $12 monthly fee. Please refund.",
            "disputed_amount": 12.0,
            "status": "RESOLVED",
            "assigned_to": "Alice Johnson",
            "root_cause": "System failed to trigger senior category automatic conversion on customer birthdate.",
            "investigation_notes": "Checked birthdate in system. Confirming age is indeed over 111. Applied senior checking waiver flag. Refunding $12.00 fee.",
            "refund_amount": 12.0,
            "goodwill_amount": 5.0,
            "interest_amount": 0.0,
            "total_redress": 17.0,
            "review_decision": "APPROVED",
            "supervisor_name": "Sarah Jenkins",
            "supervisor_notes": "Confirmed senior waiver. Bilbo is definitely eligible. Approved.",
            "sla_target_hours": 168,
            "days_ago_created": 10,
            "days_ago_resolved": 7,
            "audit_trail": [
                {"action": "CREATED", "role": "Customer", "name": "Bilbo Baggins", "details": "Phone call to representative.", "offset_days": 10},
                {"action": "ASSIGNED", "role": "Case Handler", "name": "Alice Johnson", "details": "Assigned to Alice Johnson.", "offset_days": 9},
                {"action": "INVESTIGATION_UPDATED", "role": "Case Handler", "name": "Alice Johnson", "details": "Birthdate audit complete. Flag applied.", "offset_days": 8},
                {"action": "REDRESS_CALCULATED", "role": "Case Handler", "name": "Alice Johnson", "details": "Refunding $12 and adding $5 goodwill.", "offset_days": 8, "metadata": {"refund": 12.0, "goodwill": 5.0, "interest": 0.0}},
                {"action": "STATUS_CHANGED", "role": "Case Handler", "name": "Alice Johnson", "details": "Submitting for review.", "from_status": "IN_INVESTIGATION", "to_status": "UNDER_REVIEW", "offset_days": 8},
                {"action": "SUPERVISOR_APPROVED", "role": "Supervisor", "name": "Sarah Jenkins", "details": "Senior waiver confirmed. Approved.", "offset_days": 7},
                {"action": "RESOLVED", "role": "Case Handler", "name": "Alice Johnson", "details": "Resolved. Fee reversed on ledger.", "offset_days": 7}
            ]
        },
        # 14. ESCALATED
        {
            "reference_number": "CMP-2026-014",
            "customer_name": "Bruce Wayne",
            "customer_id": "CUST-19390",
            "customer_email": "bruce@example.com",
            "customer_phone": "555-0000",
            "account_number": "ACT-100000",
            "account_type": "Credit Card",
            "product_type": "credit cards",
            "category": "Merchant Chargeback Dispute",
            "priority": "HIGH",
            "channel": "Online",
            "subject": "Disputed merchant return processing refund",
            "narrative": "I returned a customized titanium armor set worth $8,500. The merchant has provided a receipt confirming the return credit was issued to my card. However, your system has not processed the refund credit for 3 weeks.",
            "disputed_amount": 8500.0,
            "status": "ESCALATED",
            "assigned_to": "Jane Doe",
            "root_cause": None,
            "investigation_notes": "The transaction shows pending arbitration at Mastercard network level. Highly complex merchant dispute involving dual acquirer networks.",
            "refund_amount": 0.0,
            "goodwill_amount": 0.0,
            "interest_amount": 0.0,
            "total_redress": 0.0,
            "review_decision": "NONE",
            "supervisor_name": None,
            "supervisor_notes": None,
            "sla_target_hours": 72,
            "days_ago_created": 10,
            "days_ago_resolved": None,
            "audit_trail": [
                {"action": "CREATED", "role": "Customer", "name": "Bruce Wayne", "details": "Online complaint portal.", "offset_days": 10},
                {"action": "ASSIGNED", "role": "Case Handler", "name": "Jane Doe", "details": "Assigned to Jane Doe.", "offset_days": 9},
                {"action": "INVESTIGATION_UPDATED", "role": "Case Handler", "name": "Jane Doe", "details": "Requested Mastercard clearing trace file.", "offset_days": 7},
                {"action": "ESCALATED", "role": "Case Handler", "name": "Jane Doe", "details": "Escalating to Network Relations and Chargeback Dispute Board due to high amount and legal threats.", "offset_days": 5}
            ]
        },
        # 15. NEW
        {
            "reference_number": "CMP-2026-015",
            "customer_name": "Clark Kent",
            "customer_id": "CUST-19380",
            "customer_email": "clark.kent@example.com",
            "customer_phone": "555-7873",
            "account_number": "ACT-333444",
            "account_type": "Mortgage",
            "product_type": "mortgages",
            "category": "Interest Lock Dispute",
            "priority": "CRITICAL",
            "channel": "Branch",
            "subject": "Disputed Mortgage Rate Lock Expiration",
            "narrative": "I locked in an interest rate of 5.125% for my mortgage. Due to your underwriters taking too long to request simple documents, the lock expired. Now your agent is forcing me to sign at 5.75%, which costs me thousands over the loan life.",
            "disputed_amount": 18000.0,
            "status": "NEW",
            "assigned_to": None,
            "root_cause": None,
            "investigation_notes": None,
            "refund_amount": 0.0,
            "goodwill_amount": 0.0,
            "interest_amount": 0.0,
            "total_redress": 0.0,
            "review_decision": "NONE",
            "supervisor_name": None,
            "supervisor_notes": None,
            "sla_target_hours": 48,
            "days_ago_created": 1,
            "days_ago_resolved": None,
            "audit_trail": [
                {"action": "CREATED", "role": "Branch Manager", "name": "Perry White", "details": "In-person branch escalation regarding mortgage lock expiration.", "offset_days": 1}
            ]
        },
        # 16. IN_INVESTIGATION
        {
            "reference_number": "CMP-2026-016",
            "customer_name": "Barry Allen",
            "customer_id": "CUST-00200",
            "customer_email": "barry@example.com",
            "customer_phone": "555-7860",
            "account_number": "ACT-606060",
            "account_type": "Personal Loan",
            "product_type": "personal loans",
            "category": "Early Payoff Calculation",
            "priority": "MEDIUM",
            "channel": "Online",
            "subject": "Early payoff interest computation discrepancy",
            "narrative": "I requested an early payoff quote which was valid for 10 days. I paid it within 2 days, but the system still charged me interest for the full 10 days.",
            "disputed_amount": 120.0,
            "status": "IN_INVESTIGATION",
            "assigned_to": "John Smith",
            "root_cause": None,
            "investigation_notes": "Checking interest accrual job logs for date of payoff transaction.",
            "refund_amount": 0.0,
            "goodwill_amount": 0.0,
            "interest_amount": 0.0,
            "total_redress": 0.0,
            "review_decision": "NONE",
            "supervisor_name": None,
            "supervisor_notes": None,
            "sla_target_hours": 120,
            "days_ago_created": 3,
            "days_ago_resolved": None,
            "audit_trail": [
                {"action": "CREATED", "role": "Customer", "name": "Barry Allen", "details": "Online request logged.", "offset_days": 3},
                {"action": "ASSIGNED", "role": "Case Handler", "name": "John Smith", "details": "Assigned to John Smith.", "offset_days": 2}
            ]
        },
        # 17. ESCALATED
        {
            "reference_number": "CMP-2026-017",
            "customer_name": "Hal Jordan",
            "customer_id": "CUST-00900",
            "customer_email": "hal@example.com",
            "customer_phone": "555-2814",
            "account_number": "ACT-909090",
            "account_type": "Checking",
            "product_type": "fraud claims",
            "category": "Identity Theft",
            "priority": "CRITICAL",
            "channel": "Branch",
            "subject": "Account opened fraudulently using my SSN",
            "narrative": "I received a collections letter for an overdrafted account that I never opened. Someone used my SSN and a fake address. I demand this be removed from credit reports immediately.",
            "disputed_amount": 2500.0,
            "status": "ESCALATED",
            "assigned_to": "Jane Doe",
            "root_cause": None,
            "investigation_notes": "Identity theft packet received with police report. Need legal review.",
            "refund_amount": 0.0,
            "goodwill_amount": 0.0,
            "interest_amount": 0.0,
            "total_redress": 0.0,
            "review_decision": "NONE",
            "supervisor_name": None,
            "supervisor_notes": None,
            "sla_target_hours": 48,
            "days_ago_created": 5,
            "days_ago_resolved": None,
            "audit_trail": [
                {"action": "CREATED", "role": "Branch Manager", "name": "Abin Sur", "details": "In-branch complaint with police report documents.", "offset_days": 5},
                {"action": "ASSIGNED", "role": "Case Handler", "name": "Jane Doe", "details": "Assigned to Jane Doe.", "offset_days": 4},
                {"action": "ESCALATED", "role": "Case Handler", "name": "Jane Doe", "details": "Escalated to Fraud Legal Counsel.", "offset_days": 3}
            ]
        }
    ]


    # Create Database Entries
    for complaint in complaints_data:
        days_ago = complaint["days_ago_created"]
        created_time = now - datetime.timedelta(days=days_ago)
        updated_time = now - datetime.timedelta(days=days_ago) # will update as we add audit logs
        resolved_time = None
        if complaint["days_ago_resolved"] is not None:
            resolved_time = now - datetime.timedelta(days=complaint["days_ago_resolved"])

        db_complaint = models.Complaint(
            reference_number=complaint["reference_number"],
            customer_name=complaint["customer_name"],
            customer_id=complaint["customer_id"],
            customer_email=complaint["customer_email"],
            customer_phone=complaint["customer_phone"],
            account_number=complaint["account_number"],
            account_type=complaint["account_type"],
            product_type=complaint["product_type"],
            category=complaint["category"],
            priority=complaint["priority"],
            channel=complaint["channel"],
            subject=complaint["subject"],
            narrative=complaint["narrative"],
            disputed_amount=complaint["disputed_amount"],
            status=complaint["status"],
            assigned_to=complaint["assigned_to"],
            root_cause=complaint["root_cause"],
            investigation_notes=complaint["investigation_notes"],
            refund_amount=complaint["refund_amount"],
            goodwill_amount=complaint["goodwill_amount"],
            interest_amount=complaint["interest_amount"],
            total_redress=complaint["total_redress"],
            review_decision=complaint["review_decision"],
            supervisor_name=complaint["supervisor_name"],
            supervisor_notes=complaint["supervisor_notes"],
            created_at=created_time,
            updated_at=resolved_time if resolved_time else updated_time,
            sla_target_hours=complaint["sla_target_hours"],
            resolved_at=resolved_time
        )
        db.add(db_complaint)
        db.commit()
        db.refresh(db_complaint)

        # Create audit logs
        for log in complaint["audit_trail"]:
            log_time = now - datetime.timedelta(days=log["offset_days"]) if "offset_days" in log else created_time
            # Keep log times chronological
            metadata_str = json.dumps(log["metadata"]) if "metadata" in log else None
            
            from_st = log.get("from_status")
            to_st = log.get("to_status")
            # If from/to status not explicitly defined, fallback based on action
            if log["action"] == "CREATED":
                to_st = "NEW"
            elif log["action"] == "RESOLVED":
                from_st = "APPROVED"
                to_st = "RESOLVED"
            elif log["action"] == "SUPERVISOR_APPROVED":
                from_st = "UNDER_REVIEW"
                to_st = "APPROVED"
            elif log["action"] == "ESCALATED":
                from_st = "IN_INVESTIGATION"
                to_st = "ESCALATED"

            db_log = models.AuditLog(
                complaint_id=db_complaint.id,
                timestamp=log_time,
                actor_role=log["role"],
                actor_name=log["name"],
                action_type=log["action"],
                from_status=from_st,
                to_status=to_st,
                details=log["details"],
                metadata_json=metadata_str
            )
            db.add(db_log)
        
        db.commit()
