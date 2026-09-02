import React, { useState, useEffect, useMemo } from 'react'
import {
  Search,
  Plus,
  RotateCcw,
  Shield,
  ShieldAlert,
  CheckCircle,
  Clock,
  ArrowRight,
  X,
  User,
  Activity,
  FileText,
  Sparkles,
  AlertTriangle,
  UserPlus,
  Save,
  Check,
  Ban,
  ArrowDown,
  Layers,
  Lock,
  Mail,
  Phone,
  CreditCard,
  Briefcase
} from 'lucide-react'

// --- Interface Definitions ---
interface AuditLog {
  id: number;
  complaint_id: number;
  timestamp: string;
  actor_role: string;
  actor_name: string;
  action_type: string;
  from_status?: string;
  to_status?: string;
  details?: string;
}

interface Complaint {
  id: number;
  reference_number: string;
  customer_name: string;
  customer_id: string;
  customer_email: string;
  customer_phone: string;
  account_number: string;
  account_type: string;
  product_type: string;
  category: string;
  priority: string; // LOW, MEDIUM, HIGH, CRITICAL
  channel: string;
  subject: string;
  narrative: string;
  disputed_amount: number;
  status: string; // NEW, IN_INVESTIGATION, UNDER_REVIEW, APPROVED, RESOLVED, ESCALATED
  assigned_to?: string;
  root_cause?: string;
  investigation_notes?: string;
  refund_amount: number;
  goodwill_amount: number;
  interest_amount: number;
  total_redress: number;
  supervisor_notes?: string;
  review_decision: string; // APPROVED, REJECTED, NONE
  supervisor_name?: string;
  created_at: string;
  updated_at: string;
  sla_target_hours: number;
  resolved_at?: string;
  audit_logs: AuditLog[];
}

interface WorkbenchStats {
  total: number;
  under_review: number;
  in_investigation: number;
  resolved: number;
  escalated: number;
  total_redress_paid: number;
}

interface ToastMessage {
  id: string;
  message: string;
  type: 'success' | 'error' | 'info';
}

// --- Constants & Options ---
const ROLES = [
  'Intake Specialist',
  'Case Handler / Investigator',
  'Supervisor',
  'Compliance Auditor'
] as const;

type Role = typeof ROLES[number];

const ROLE_ACTORS: Record<Role, { name: string; tag: string }> = {
  'Intake Specialist': { name: 'Alice Smith', tag: 'INTAKE' },
  'Case Handler / Investigator': { name: 'Bob Jones', tag: 'INVESTIGATOR' },
  'Supervisor': { name: 'Sarah Conner', tag: 'SUPERVISOR' },
  'Compliance Auditor': { name: 'Eleanor Rigby', tag: 'AUDITOR' }
};

const STAGES = [
  { key: 'NEW', label: 'New / Intake', color: 'border-blue-500 bg-blue-50/10 text-blue-700' },
  { key: 'IN_INVESTIGATION', label: 'In Investigation', color: 'border-indigo-500 bg-indigo-50/10 text-indigo-700' },
  { key: 'UNDER_REVIEW', label: 'Under Supervisor Review', color: 'border-amber-500 bg-amber-50/10 text-amber-700' },
  { key: 'APPROVED', label: 'Approved', color: 'border-emerald-500 bg-emerald-50/10 text-emerald-700' },
  { key: 'RESOLVED', label: 'Resolved', color: 'border-teal-500 bg-teal-50/10 text-teal-700' },
  { key: 'ESCALATED', label: 'Escalated', color: 'border-red-500 bg-red-50/10 text-red-700' }
];

const PRIORITIES = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'] as const;
const PRODUCTS = ['Checking', 'Credit Card', 'Mortgage', 'Loan', 'Wire Transfer', 'Savings'] as const;
const ACCOUNT_TYPES = ['Checking', 'Savings', 'Credit Card', 'Mortgage', 'Business Account'] as const;
const CHANNELS = ['Branch', 'Phone', 'Online Banking', 'Mobile App', 'Written Letter'] as const;

const ROOT_CAUSES = [
  'Bank System Issue',
  'Operational Error',
  'Policy Dispute',
  'Customer Misunderstanding',
  'Third-Party Fraud'
];

const CATEGORIES = [
  'Unauthorized Transaction',
  'Overdraft Fee Dispute',
  'Delayed Wire Transfer',
  'Incorrect Billing',
  'Poor Branch Service',
  'Loan Servicing Error'
];

// --- Synthetic In-Memory / LocalStorage Seeder Data ---
const SEED_COMPLAINTS: Complaint[] = [
  {
    id: 1,
    reference_number: 'CMP-2026-001',
    customer_name: 'John Doe',
    customer_id: 'CUST-1092',
    customer_email: 'john.doe@synthetic.bank.com',
    customer_phone: '+1 (555) 019-2831',
    account_number: 'ACCT-8849-012',
    account_type: 'Checking',
    product_type: 'Checking',
    category: 'Unauthorized Transaction',
    priority: 'HIGH',
    channel: 'Online Banking',
    subject: 'Unauthorized ATM Withdrawal',
    narrative: 'A withdrawal of $450 was made from my account at an ATM in Chicago yesterday, but I was in New York. I still have my physical card with me. I suspect card skimming or cloning.',
    disputed_amount: 450.00,
    status: 'NEW',
    refund_amount: 0.0,
    goodwill_amount: 0.0,
    interest_amount: 0.0,
    total_redress: 0.0,
    review_decision: 'NONE',
    created_at: new Date(Date.now() - 36 * 3600 * 1000).toISOString(), // 36h ago
    updated_at: new Date(Date.now() - 36 * 3600 * 1000).toISOString(),
    sla_target_hours: 168,
    audit_logs: [
      {
        id: 101,
        complaint_id: 1,
        timestamp: new Date(Date.now() - 36 * 3600 * 1000).toISOString(),
        actor_role: 'Intake Specialist',
        actor_name: 'Alice Smith',
        action_type: 'CREATED',
        from_status: 'NONE',
        to_status: 'NEW',
        details: 'Complaint recorded with HIGH severity. Case unassigned.'
      }
    ]
  },
  {
    id: 2,
    reference_number: 'CMP-2026-002',
    customer_name: 'Jane Miller',
    customer_id: 'CUST-3841',
    customer_email: 'jane.miller@synthetic.bank.com',
    customer_phone: '+1 (555) 012-9912',
    account_number: 'ACCT-3948-281',
    account_type: 'Business Account',
    product_type: 'Wire Transfer',
    category: 'Delayed Wire Transfer',
    priority: 'CRITICAL',
    channel: 'Branch',
    subject: 'Delayed Wire Transfer to Escrow',
    narrative: 'My business initiated a time-critical wire transfer of $125,000 for a real estate purchase escrow. The funds left our account, but the recipient escrow agent has not received them. The closing deadline is today, and we risk breach of contract penalties!',
    disputed_amount: 125000.00,
    status: 'IN_INVESTIGATION',
    assigned_to: 'Bob Jones',
    root_cause: 'Bank System Issue',
    investigation_notes: 'Investigating delay in Federal Reserve wire room routing. Fedwire was offline briefly during transaction. Traced wire reference ID #W-9921838. Wire is currently stuck in queue.',
    refund_amount: 0.0,
    goodwill_amount: 0.0,
    interest_amount: 0.0,
    total_redress: 0.0,
    review_decision: 'NONE',
    created_at: new Date(Date.now() - 6 * 24 * 3600 * 1000).toISOString(), // 6 days ago (SLA Warning)
    updated_at: new Date(Date.now() - 2 * 24 * 3600 * 1000).toISOString(),
    sla_target_hours: 168,
    audit_logs: [
      {
        id: 201,
        complaint_id: 2,
        timestamp: new Date(Date.now() - 6 * 24 * 3600 * 1000).toISOString(),
        actor_role: 'Intake Specialist',
        actor_name: 'Alice Smith',
        action_type: 'CREATED',
        from_status: 'NONE',
        to_status: 'NEW',
        details: 'Complaint logged at branch level.'
      },
      {
        id: 202,
        complaint_id: 2,
        timestamp: new Date(Date.now() - 5.5 * 24 * 3600 * 1000).toISOString(),
        actor_role: 'Case Handler / Investigator',
        actor_name: 'Bob Jones',
        action_type: 'ASSIGNED',
        details: 'Case claimed and assigned to Bob Jones.'
      },
      {
        id: 203,
        complaint_id: 2,
        timestamp: new Date(Date.now() - 5.5 * 24 * 3600 * 1000).toISOString(),
        actor_role: 'Case Handler / Investigator',
        actor_name: 'Bob Jones',
        action_type: 'STATUS_CHANGED',
        from_status: 'NEW',
        to_status: 'IN_INVESTIGATION',
        details: 'Status transitioned to Investigation.'
      }
    ]
  },
  {
    id: 3,
    reference_number: 'CMP-2026-003',
    customer_name: 'Robert Smith',
    customer_id: 'CUST-8831',
    customer_email: 'bob.smith@synthetic.bank.com',
    customer_phone: '+1 (555) 014-4481',
    account_number: 'CARD-9921-884',
    account_type: 'Credit Card',
    product_type: 'Credit Card',
    category: 'Incorrect Billing',
    priority: 'MEDIUM',
    channel: 'Mobile App',
    subject: 'Credit Card Overlimit Fee Dispute',
    narrative: 'I was charged a $35 overlimit fee on my July statement, but my balance never exceeded my $5,000 limit. I did a calculation of all transactions, and at no point was I over the limit. This seems to be a system error.',
    disputed_amount: 35.00,
    status: 'UNDER_REVIEW',
    assigned_to: 'Jane Doe',
    root_cause: 'Bank System Issue',
    investigation_notes: 'System calculated a pending hold twice, erroneously pushing the internal balance metric above $5,000 for 12 hours. Hold was subsequently cleared but overlimit fee was batch-processed.',
    refund_amount: 35.00,
    goodwill_amount: 15.00,
    interest_amount: 0.00,
    total_redress: 50.00,
    review_decision: 'NONE',
    created_at: new Date(Date.now() - 2 * 24 * 3600 * 1000).toISOString(), // 2 days ago
    updated_at: new Date(Date.now() - 4 * 3600 * 1000).toISOString(),
    sla_target_hours: 168,
    audit_logs: [
      {
        id: 301,
        complaint_id: 3,
        timestamp: new Date(Date.now() - 2 * 24 * 3600 * 1000).toISOString(),
        actor_role: 'Intake Specialist',
        actor_name: 'Alice Smith',
        action_type: 'CREATED',
        from_status: 'NONE',
        to_status: 'NEW',
        details: 'Digital mobile app complaint logged.'
      },
      {
        id: 302,
        complaint_id: 3,
        timestamp: new Date(Date.now() - 1.8 * 24 * 3600 * 1000).toISOString(),
        actor_role: 'Case Handler / Investigator',
        actor_name: 'Jane Doe',
        action_type: 'ASSIGNED',
        details: 'Assigned to Jane Doe.'
      },
      {
        id: 303,
        complaint_id: 3,
        timestamp: new Date(Date.now() - 1.8 * 24 * 3600 * 1000).toISOString(),
        actor_role: 'Case Handler / Investigator',
        actor_name: 'Jane Doe',
        action_type: 'STATUS_CHANGED',
        from_status: 'NEW',
        to_status: 'IN_INVESTIGATION',
        details: 'Investigation initiated.'
      },
      {
        id: 304,
        complaint_id: 3,
        timestamp: new Date(Date.now() - 4 * 3600 * 1000).toISOString(),
        actor_role: 'Case Handler / Investigator',
        actor_name: 'Jane Doe',
        action_type: 'REDRESS_LOGGED',
        details: 'Proposed redress: $35.00 Refund, $15.00 Goodwill compensation.'
      },
      {
        id: 305,
        complaint_id: 3,
        timestamp: new Date(Date.now() - 4 * 3600 * 1000).toISOString(),
        actor_role: 'Case Handler / Investigator',
        actor_name: 'Jane Doe',
        action_type: 'STATUS_CHANGED',
        from_status: 'IN_INVESTIGATION',
        to_status: 'UNDER_REVIEW',
        details: 'Resolution proposed and submitted for Supervisor sign-off.'
      }
    ]
  },
  {
    id: 4,
    reference_number: 'CMP-2026-004',
    customer_name: 'Emily Davis',
    customer_id: 'CUST-4912',
    customer_email: 'emily.davis@synthetic.bank.com',
    customer_phone: '+1 (555) 019-3382',
    account_number: 'ACCT-1122-334',
    account_type: 'Savings',
    product_type: 'Savings',
    category: 'Poor Branch Service',
    priority: 'LOW',
    channel: 'Written Letter',
    subject: 'Branch Manager Service Dispute',
    narrative: 'I went to the Downtown branch to request an estate payout for my late aunt. The manager was extremely rude, kept me waiting for 2 hours, and initially refused to accept valid probate letters, questioning my identity in public. It was a humiliating experience during a time of grief.',
    disputed_amount: 0.00,
    status: 'APPROVED',
    assigned_to: 'Bob Jones',
    root_cause: 'Operational Error',
    investigation_notes: 'Spoke with Downtown branch branch manager. There was a staff misunderstanding of probate requirements for minor estate thresholds. While legal procedures are strict, staff behavior was suboptimal and lacked empathy.',
    refund_amount: 0.0,
    goodwill_amount: 100.0,
    interest_amount: 0.0,
    total_redress: 100.0,
    review_decision: 'APPROVED',
    supervisor_name: 'Sarah Conner',
    supervisor_notes: 'SUBOPTIMAL STAFF BEHAVIOR CONFIRMED. Full probate policy training scheduled for branch team. Approved goodwill gesture of $100 with official apology letter.',
    created_at: new Date(Date.now() - 8 * 24 * 3600 * 1000).toISOString(), // 8 days ago (SLA Overdue)
    updated_at: new Date(Date.now() - 1 * 24 * 3600 * 1000).toISOString(),
    sla_target_hours: 168,
    audit_logs: [
      {
        id: 401,
        complaint_id: 4,
        timestamp: new Date(Date.now() - 8 * 24 * 3600 * 1000).toISOString(),
        actor_role: 'Intake Specialist',
        actor_name: 'Alice Smith',
        action_type: 'CREATED',
        from_status: 'NONE',
        to_status: 'NEW',
        details: 'Recorded via physical written grievance letter scan.'
      },
      {
        id: 402,
        complaint_id: 4,
        timestamp: new Date(Date.now() - 7 * 24 * 3600 * 1000).toISOString(),
        actor_role: 'Case Handler / Investigator',
        actor_name: 'Bob Jones',
        action_type: 'ASSIGNED',
        details: 'Assigned to Bob Jones.'
      },
      {
        id: 403,
        complaint_id: 4,
        timestamp: new Date(Date.now() - 7 * 24 * 3600 * 1000).toISOString(),
        actor_role: 'Case Handler / Investigator',
        actor_name: 'Bob Jones',
        action_type: 'STATUS_CHANGED',
        from_status: 'NEW',
        to_status: 'IN_INVESTIGATION',
        details: 'Investigation started.'
      },
      {
        id: 404,
        complaint_id: 4,
        timestamp: new Date(Date.now() - 3 * 24 * 3600 * 1000).toISOString(),
        actor_role: 'Case Handler / Investigator',
        actor_name: 'Bob Jones',
        action_type: 'REDRESS_LOGGED',
        details: 'Goodwill redress of $100.00 entered.'
      },
      {
        id: 405,
        complaint_id: 4,
        timestamp: new Date(Date.now() - 3 * 24 * 3600 * 1000).toISOString(),
        actor_role: 'Case Handler / Investigator',
        actor_name: 'Bob Jones',
        action_type: 'STATUS_CHANGED',
        from_status: 'IN_INVESTIGATION',
        to_status: 'UNDER_REVIEW',
        details: 'Forwarded for Supervisor approval.'
      },
      {
        id: 406,
        complaint_id: 4,
        timestamp: new Date(Date.now() - 1 * 24 * 3600 * 1000).toISOString(),
        actor_role: 'Supervisor',
        actor_name: 'Sarah Conner',
        action_type: 'SUPERVISOR_DECISION',
        from_status: 'UNDER_REVIEW',
        to_status: 'APPROVED',
        details: 'Approved with note: SUBOPTIMAL STAFF BEHAVIOR CONFIRMED. Payout processing.'
      }
    ]
  },
  {
    id: 5,
    reference_number: 'CMP-2026-005',
    customer_name: 'Michael Wilson',
    customer_id: 'CUST-5512',
    customer_email: 'm.wilson@synthetic.bank.com',
    customer_phone: '+1 (555) 011-8841',
    account_number: 'ACCT-5566-778',
    account_type: 'Mortgage',
    product_type: 'Mortgage',
    category: 'Incorrect Billing',
    priority: 'MEDIUM',
    channel: 'Phone',
    subject: 'Mortgage Application Fee Double Charge',
    narrative: 'I paid a mortgage application processing fee of $250 online, but on checking my bank statement, I noticed it was charged twice on July 15 and July 16. I want the extra charge refunded with interest.',
    disputed_amount: 250.00,
    status: 'RESOLVED',
    assigned_to: 'Jane Doe',
    root_cause: 'Operational Error',
    investigation_notes: 'Verified transaction double payment. Card reader was clicked twice by agent under stress. Full refund of $250.00 processed plus $5.42 statutory interest correction.',
    refund_amount: 250.00,
    goodwill_amount: 50.00,
    interest_amount: 5.42,
    total_redress: 305.42,
    review_decision: 'APPROVED',
    supervisor_name: 'Sarah Conner',
    supervisor_notes: 'Valid billing error. Redress is highly accurate.',
    resolved_at: new Date(Date.now() - 1 * 24 * 3600 * 1000).toISOString(),
    created_at: new Date(Date.now() - 10 * 24 * 3600 * 1000).toISOString(),
    updated_at: new Date(Date.now() - 1 * 24 * 3600 * 1000).toISOString(),
    sla_target_hours: 168,
    audit_logs: [
      {
        id: 501,
        complaint_id: 5,
        timestamp: new Date(Date.now() - 10 * 24 * 3600 * 1000).toISOString(),
        actor_role: 'Intake Specialist',
        actor_name: 'Alice Smith',
        action_type: 'CREATED',
        from_status: 'NONE',
        to_status: 'NEW',
        details: 'Phone complaint filed.'
      },
      {
        id: 502,
        complaint_id: 5,
        timestamp: new Date(Date.now() - 9 * 24 * 3600 * 1000).toISOString(),
        actor_role: 'Case Handler / Investigator',
        actor_name: 'Jane Doe',
        action_type: 'ASSIGNED',
        details: 'Assigned to Jane Doe.'
      },
      {
        id: 503,
        complaint_id: 5,
        timestamp: new Date(Date.now() - 9 * 24 * 3600 * 1000).toISOString(),
        actor_role: 'Case Handler / Investigator',
        actor_name: 'Jane Doe',
        action_type: 'STATUS_CHANGED',
        from_status: 'NEW',
        to_status: 'IN_INVESTIGATION',
        details: 'Investigating billing logs.'
      },
      {
        id: 504,
        complaint_id: 5,
        timestamp: new Date(Date.now() - 4 * 24 * 3600 * 1000).toISOString(),
        actor_role: 'Case Handler / Investigator',
        actor_name: 'Jane Doe',
        action_type: 'REDRESS_LOGGED',
        details: 'Refund: $250, Goodwill: $50, Interest: $5.42.'
      },
      {
        id: 505,
        complaint_id: 5,
        timestamp: new Date(Date.now() - 4 * 24 * 3600 * 1000).toISOString(),
        actor_role: 'Case Handler / Investigator',
        actor_name: 'Jane Doe',
        action_type: 'STATUS_CHANGED',
        from_status: 'IN_INVESTIGATION',
        to_status: 'UNDER_REVIEW',
        details: 'Submitted for sign-off.'
      },
      {
        id: 506,
        complaint_id: 5,
        timestamp: new Date(Date.now() - 2 * 24 * 3600 * 1000).toISOString(),
        actor_role: 'Supervisor',
        actor_name: 'Sarah Conner',
        action_type: 'SUPERVISOR_DECISION',
        from_status: 'UNDER_REVIEW',
        to_status: 'APPROVED',
        details: 'Approved by Sarah Conner.'
      },
      {
        id: 507,
        complaint_id: 5,
        timestamp: new Date(Date.now() - 1 * 24 * 3600 * 1000).toISOString(),
        actor_role: 'Case Handler / Investigator',
        actor_name: 'Jane Doe',
        action_type: 'STATUS_CHANGED',
        from_status: 'APPROVED',
        to_status: 'RESOLVED',
        details: 'Payout successfully settled with customer. Complaint closed.'
      }
    ]
  },
  {
    id: 6,
    reference_number: 'CMP-2026-006',
    customer_name: 'David Brown',
    customer_id: 'CUST-4419',
    customer_email: 'david.brown@synthetic.bank.com',
    customer_phone: '+1 (555) 018-9128',
    account_number: 'CARD-4433-221',
    account_type: 'Credit Card',
    product_type: 'Credit Card',
    category: 'Unauthorized Transaction',
    priority: 'CRITICAL',
    channel: 'Phone',
    subject: 'Suspected Identity Theft Dispute',
    narrative: 'I received multiple SMS alerts for charges totaling $8,400 at a high-end electronics store in Paris. I have never been to Europe and my card is in my pocket. I immediately phoned customer support to freeze the card. This must be identity theft or cloned credentials.',
    disputed_amount: 8400.00,
    status: 'ESCALATED',
    assigned_to: 'Jane Doe',
    root_cause: 'Third-Party Fraud',
    investigation_notes: 'Confirmed cards were skimmed. Fraud pattern matched massive local merchant breach. Escalated to Security / Cyber Fraud Investigation Division for law enforcement collaboration.',
    refund_amount: 0.0,
    goodwill_amount: 0.0,
    interest_amount: 0.0,
    total_redress: 0.0,
    review_decision: 'NONE',
    created_at: new Date(Date.now() - 1 * 24 * 3600 * 1000).toISOString(), // 1 day ago
    updated_at: new Date(Date.now() - 12 * 3600 * 1000).toISOString(),
    sla_target_hours: 168,
    audit_logs: [
      {
        id: 601,
        complaint_id: 6,
        timestamp: new Date(Date.now() - 1 * 24 * 3600 * 1000).toISOString(),
        actor_role: 'Intake Specialist',
        actor_name: 'Alice Smith',
        action_type: 'CREATED',
        from_status: 'NONE',
        to_status: 'NEW',
        details: 'Urgent security breach complaint.'
      },
      {
        id: 602,
        complaint_id: 6,
        timestamp: new Date(Date.now() - 22 * 3600 * 1000).toISOString(),
        actor_role: 'Case Handler / Investigator',
        actor_name: 'Jane Doe',
        action_type: 'ASSIGNED',
        details: 'Assigned to Jane Doe.'
      },
      {
        id: 603,
        complaint_id: 6,
        timestamp: new Date(Date.now() - 22 * 3600 * 1000).toISOString(),
        actor_role: 'Case Handler / Investigator',
        actor_name: 'Jane Doe',
        action_type: 'STATUS_CHANGED',
        from_status: 'NEW',
        to_status: 'IN_INVESTIGATION',
        details: 'Investigation initiated. Card blocked.'
      },
      {
        id: 604,
        complaint_id: 6,
        timestamp: new Date(Date.now() - 12 * 3600 * 1000).toISOString(),
        actor_role: 'Case Handler / Investigator',
        actor_name: 'Jane Doe',
        action_type: 'STATUS_CHANGED',
        from_status: 'IN_INVESTIGATION',
        to_status: 'ESCALATED',
        details: 'Escalated to specialized Security Fraud Unit due to potential systemic skimming ring.'
      }
    ]
  }
];

// --- Application Entry Point ---
export default function App() {
  // --- Toast Management ---
  const [toasts, setToasts] = useState<ToastMessage[]>([]);
  const showToast = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 4000);
  };

  // --- Active Role / Actor Context ---
  const [activeRole, setActiveRole] = useState<Role>('Intake Specialist');
  const activeActor = useMemo(() => ROLE_ACTORS[activeRole], [activeRole]);

  // --- Complaints Database State ---
  const [complaints, setComplaints] = useState<Complaint[]>([]);
  const [loading, setLoading] = useState(true);

  // --- Filters & Search State ---
  const [searchQuery, setSearchQuery] = useState('');
  const [priorityFilter, setPriorityFilter] = useState<string>('ALL');
  const [productFilter, setProductFilter] = useState<string>('ALL');
  const [handlerFilter, setHandlerFilter] = useState<string>('ALL');

  // --- Modal / Drawer Active States ---
  const [isIntakeOpen, setIsIntakeOpen] = useState(false);
  const [selectedComplaintId, setSelectedComplaintId] = useState<number | null>(null);

  // --- Detail Drawer Local Field States ---
  const [rootCauseInput, setRootCauseInput] = useState('');
  const [notesInput, setInvestigationNotesInput] = useState('');
  const [refundInput, setRefundInput] = useState('');
  const [goodwillInput, setGoodwillInput] = useState('');
  const [interestInput, setInterestInput] = useState('');
  const [supervisorNotesInput, setSupervisorNotesInput] = useState('');
  const [rejectionWarning, setRejectionWarning] = useState(false);

  // --- Load Complaints & Handle API + LocalStorage Fallback ---
  const fetchComplaints = async (showNotification = false) => {
    setLoading(true);
    try {
      const response = await fetch('/api/complaints');
      if (response.ok) {
        const data = await response.json();
        setComplaints(data);
        if (showNotification) showToast('Data loaded from SQLite backend database.', 'success');
      } else {
        throw new Error('Backend failed');
      }
    } catch (error) {
      console.warn('Backend unavailable, using Local Storage fallback.', error);
      // Fallback to LocalStorage
      const local = localStorage.getItem('agy_workbench_complaints');
      if (local) {
        setComplaints(JSON.parse(local));
      } else {
        // First load seeder initialization
        localStorage.setItem('agy_workbench_complaints', JSON.stringify(SEED_COMPLAINTS));
        setComplaints(SEED_COMPLAINTS);
      }
      if (showNotification) showToast('Data synced with persistent Local Storage.', 'info');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchComplaints();
  }, []);

  // --- Write to LocalStorage helper for falls backs ---
  const saveLocalState = (updatedComplaints: Complaint[]) => {
    localStorage.setItem('agy_workbench_complaints', JSON.stringify(updatedComplaints));
    setComplaints(updatedComplaints);
  };

  // --- Reset/Seed Database API/Local ---
  const handleResetData = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/seed', { method: 'POST' });
      if (response.ok) {
        showToast('Database reset successfully with synthetic data.', 'success');
        await fetchComplaints();
      } else {
        throw new Error('Seed endpoint failed');
      }
    } catch (error) {
      console.warn('Backend seed failed, resetting Local Storage state.', error);
      saveLocalState(SEED_COMPLAINTS);
      showToast('Local Storage reset successfully with 6 diverse complaints.', 'success');
    } finally {
      setLoading(false);
    }
  };

  // --- Auto-calculated SLA Details ---
  const getSLADetails = (complaint: Complaint) => {
    const created = new Date(complaint.created_at).getTime();
    const target = created + complaint.sla_target_hours * 3600 * 1000;
    const now = Date.now();
    const isResolved = complaint.status === 'RESOLVED';
    
    if (isResolved) {
      return { label: 'SLA Met', color: 'bg-green-100 text-green-800 border-green-200', overdue: false };
    }

    const remainingMs = target - now;
    const remainingHours = Math.round(remainingMs / (3600 * 1000));

    if (remainingHours < 0) {
      return {
        label: `Overdue by ${Math.abs(remainingHours)}h`,
        color: 'bg-red-100 text-red-800 border-red-200 animate-pulse font-semibold',
        overdue: true
      };
    } else if (remainingHours <= 24) {
      return {
        label: `${remainingHours}h remaining`,
        color: 'bg-amber-100 text-amber-800 border-amber-200 font-medium',
        overdue: false
      };
    } else {
      return {
        label: `${remainingHours}h left`,
        color: 'bg-emerald-100 text-emerald-800 border-emerald-200',
        overdue: false
      };
    }
  };

  // --- Search and Filtering Logic ---
  const filteredComplaints = useMemo(() => {
    return complaints.filter((c) => {
      const matchesSearch =
        c.reference_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.customer_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.subject.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.customer_id.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesPriority = priorityFilter === 'ALL' || c.priority === priorityFilter;
      const matchesProduct = productFilter === 'ALL' || c.product_type === productFilter;
      
      let matchesHandler = true;
      if (handlerFilter === 'UNASSIGNED') {
        matchesHandler = !c.assigned_to;
      } else if (handlerFilter !== 'ALL') {
        matchesHandler = c.assigned_to === handlerFilter;
      }

      return matchesSearch && matchesPriority && matchesProduct && matchesHandler;
    });
  }, [complaints, searchQuery, priorityFilter, productFilter, handlerFilter]);

  // --- Dynamic Live Stats Summary Bar ---
  const stats = useMemo<WorkbenchStats>(() => {
    let total = complaints.length;
    let under_review = 0;
    let in_investigation = 0;
    let resolved = 0;
    let escalated = 0;
    let total_redress_paid = 0.0;

    complaints.forEach((c) => {
      if (c.status === 'UNDER_REVIEW') under_review++;
      if (c.status === 'IN_INVESTIGATION') in_investigation++;
      if (c.status === 'RESOLVED') {
        resolved++;
        total_redress_paid += c.total_redress;
      }
      if (c.status === 'APPROVED') {
        total_redress_paid += c.total_redress; // Count redress from approved as paid/committed
      }
      if (c.status === 'ESCALATED') escalated++;
    });

    return { total, under_review, in_investigation, resolved, escalated, total_redress_paid };
  }, [complaints]);

  // --- List of active assigned handlers in database for filters ---
  const availableHandlers = useMemo(() => {
    const list = new Set<string>();
    complaints.forEach((c) => {
      if (c.assigned_to) list.add(c.assigned_to);
    });
    return Array.from(list);
  }, [complaints]);

  // --- Detail Drawer Selected Complaint Selection ---
  const selectedComplaint = useMemo(() => {
    return complaints.find((c) => c.id === selectedComplaintId) || null;
  }, [complaints, selectedComplaintId]);

  // --- Synchronize Drawer inputs when active case changes ---
  useEffect(() => {
    if (selectedComplaint) {
      setRootCauseInput(selectedComplaint.root_cause || '');
      setInvestigationNotesInput(selectedComplaint.investigation_notes || '');
      setRefundInput(selectedComplaint.refund_amount > 0 ? selectedComplaint.refund_amount.toString() : '');
      setGoodwillInput(selectedComplaint.goodwill_amount > 0 ? selectedComplaint.goodwill_amount.toString() : '');
      setInterestInput(selectedComplaint.interest_amount > 0 ? selectedComplaint.interest_amount.toString() : '');
      setSupervisorNotesInput(selectedComplaint.supervisor_notes || '');
      setRejectionWarning(false);
    }
  }, [selectedComplaintId, selectedComplaint]);

  // --- Reactively compute live redress calculation ---
  const liveTotalRedress = useMemo(() => {
    const r = parseFloat(refundInput) || 0;
    const g = parseFloat(goodwillInput) || 0;
    const i = parseFloat(interestInput) || 0;
    return parseFloat((r + g + i).toFixed(2));
  }, [refundInput, goodwillInput, interestInput]);

  // --- Claim Case (Assign to Self) ---
  const handleClaimCase = async (complaintId: number) => {
    try {
      const response = await fetch(`/api/complaints/${complaintId}/assign`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          assigned_to: activeActor.name,
          actor_role: activeRole,
          actor_name: activeActor.name,
          details: `Claimed case in ${activeRole} workspace.`
        })
      });

      if (response.ok) {
        showToast(`Case assigned to you.`, 'success');
        await fetchComplaints();
      } else {
        throw new Error('API Assign Failed');
      }
    } catch (error) {
      console.warn('API call failed, running in Local Storage fallback mode.', error);
      const list = complaints.map((c) => {
        if (c.id === complaintId) {
          const oldStatus = c.status;
          let targetStatus = c.status;
          
          // Auto move to IN_INVESTIGATION if in NEW
          if (c.status === 'NEW') {
            targetStatus = 'IN_INVESTIGATION';
          }

          const newLogs: AuditLog[] = [
            ...c.audit_logs,
            {
              id: Date.now() + 1,
              complaint_id: c.id,
              timestamp: new Date().toISOString(),
              actor_role: activeRole,
              actor_name: activeActor.name,
              action_type: 'ASSIGNED',
              details: `Claimed case. Assigned to ${activeActor.name}.`
            }
          ];

          if (oldStatus !== targetStatus) {
            newLogs.push({
              id: Date.now() + 2,
              complaint_id: c.id,
              timestamp: new Date().toISOString(),
              actor_role: activeRole,
              actor_name: activeActor.name,
              action_type: 'STATUS_CHANGED',
              from_status: oldStatus,
              to_status: targetStatus,
              details: `Moved from ${oldStatus} to ${targetStatus} upon claiming.`
            });
          }

          return {
            ...c,
            assigned_to: activeActor.name,
            status: targetStatus,
            updated_at: new Date().toISOString(),
            audit_logs: newLogs
          };
        }
        return c;
      });
      saveLocalState(list);
      showToast(`Case claimed successfully (Local Sync).`, 'success');
    }
  };

  // --- Drag and drop state transitions or click quick move ---
  const handleMoveStatus = async (complaintId: number, targetStatus: string) => {
    try {
      const response = await fetch(`/api/complaints/${complaintId}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: targetStatus,
          actor_role: activeRole,
          actor_name: activeActor.name,
          details: `Manual workbench stage move to ${targetStatus}.`
        })
      });

      if (response.ok) {
        showToast(`Moved to ${targetStatus}.`, 'success');
        await fetchComplaints();
      } else {
        throw new Error('API Move Status Failed');
      }
    } catch (error) {
      console.warn('API call failed, executing fallback state transition.', error);
      const list = complaints.map((c) => {
        if (c.id === complaintId) {
          const from_status = c.status;
          return {
            ...c,
            status: targetStatus,
            updated_at: new Date().toISOString(),
            audit_logs: [
              ...c.audit_logs,
              {
                id: Date.now(),
                complaint_id: c.id,
                timestamp: new Date().toISOString(),
                actor_role: activeRole,
                actor_name: activeActor.name,
                action_type: 'STATUS_CHANGED',
                from_status,
                to_status: targetStatus,
                details: `Manually moved from ${from_status} to ${targetStatus}.`
              }
            ]
          };
        }
        return c;
      });
      saveLocalState(list);
      showToast(`Moved to ${targetStatus} successfully.`, 'success');
    }
  };

  // --- Save Investigation Findings Notes / Root Cause ---
  const handleSaveFindings = async () => {
    if (!selectedComplaintId) return;
    if (!rootCauseInput || !notesInput) {
      showToast('Please select a root cause and write investigation findings first.', 'error');
      return;
    }

    try {
      const response = await fetch(`/api/complaints/${selectedComplaintId}/investigation`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          root_cause: rootCauseInput,
          investigation_notes: notesInput,
          actor_role: activeRole,
          actor_name: activeActor.name
        })
      });

      if (response.ok) {
        showToast('Investigation findings saved successfully.', 'success');
        await fetchComplaints();
      } else {
        throw new Error('Investigation save failed');
      }
    } catch (error) {
      console.warn('Investigation API failed, running fallback save.', error);
      const list = complaints.map((c) => {
        if (c.id === selectedComplaintId) {
          return {
            ...c,
            root_cause: rootCauseInput,
            investigation_notes: notesInput,
            updated_at: new Date().toISOString(),
            audit_logs: [
              ...c.audit_logs,
              {
                id: Date.now(),
                complaint_id: c.id,
                timestamp: new Date().toISOString(),
                actor_role: activeRole,
                actor_name: activeActor.name,
                action_type: 'INVESTIGATION_LOGGED',
                details: `Findings logged. Root Cause: ${rootCauseInput}`
              }
            ]
          };
        }
        return c;
      });
      saveLocalState(list);
      showToast('Findings recorded securely.', 'success');
    }
  };

  // --- Save Redress Proposal ---
  const handleSaveRedress = async () => {
    if (!selectedComplaintId) return;
    const r = parseFloat(refundInput) || 0;
    const g = parseFloat(goodwillInput) || 0;
    const i = parseFloat(interestInput) || 0;

    try {
      const response = await fetch(`/api/complaints/${selectedComplaintId}/redress`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          refund_amount: r,
          goodwill_amount: g,
          interest_amount: i,
          actor_role: activeRole,
          actor_name: activeActor.name
        })
      });

      if (response.ok) {
        showToast('Financial redress calculated and saved.', 'success');
        await fetchComplaints();
      } else {
        throw new Error('Redress save failed');
      }
    } catch (error) {
      console.warn('Redress API failed, running fallback calculate.', error);
      const list = complaints.map((c) => {
        if (c.id === selectedComplaintId) {
          return {
            ...c,
            refund_amount: r,
            goodwill_amount: g,
            interest_amount: i,
            total_redress: liveTotalRedress,
            updated_at: new Date().toISOString(),
            audit_logs: [
              ...c.audit_logs,
              {
                id: Date.now(),
                complaint_id: c.id,
                timestamp: new Date().toISOString(),
                actor_role: activeRole,
                actor_name: activeActor.name,
                action_type: 'REDRESS_LOGGED',
                details: `Proposed financial redress saved. Refund: $${r.toFixed(2)}, Goodwill: $${g.toFixed(2)}, Interest: $${i.toFixed(2)}. Total Redress: $${liveTotalRedress.toFixed(2)}.`
              }
            ]
          };
        }
        return c;
      });
      saveLocalState(list);
      showToast('Proposed financial calculations updated.', 'success');
    }
  };

  // --- Submit to Supervisor for Review ---
  const handleSubmitForReview = async () => {
    if (!selectedComplaint) return;
    if (!selectedComplaint.root_cause || !selectedComplaint.investigation_notes) {
      showToast('Cannot submit for review. Investigation Findings & Root Cause must be entered and saved first!', 'error');
      return;
    }
    if (selectedComplaint.total_redress <= 0 && selectedComplaint.disputed_amount > 0) {
      if (!confirm('You are proposing $0.00 redress for a disputed financial complaint. Proceed with submission?')) {
        return;
      }
    }

    try {
      const response = await fetch(`/api/complaints/${selectedComplaintId}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: 'UNDER_REVIEW',
          actor_role: activeRole,
          actor_name: activeActor.name,
          details: 'Submitted case file for Supervisor review and resolution validation.'
        })
      });

      if (response.ok) {
        showToast('Complaint forwarded to Supervisor for official review.', 'success');
        await fetchComplaints();
      } else {
        throw new Error('API submission failed');
      }
    } catch (error) {
      console.warn('Submit API failed, executing fallback status transition.', error);
      const list = complaints.map((c) => {
        if (c.id === selectedComplaint.id) {
          return {
            ...c,
            status: 'UNDER_REVIEW',
            updated_at: new Date().toISOString(),
            audit_logs: [
              ...c.audit_logs,
              {
                id: Date.now(),
                complaint_id: c.id,
                timestamp: new Date().toISOString(),
                actor_role: activeRole,
                actor_name: activeActor.name,
                action_type: 'STATUS_CHANGED',
                from_status: 'IN_INVESTIGATION',
                to_status: 'UNDER_REVIEW',
                details: 'Submitted case file for Supervisor review and resolution sign-off.'
              }
            ]
          };
        }
        return c;
      });
      saveLocalState(list);
      showToast('Forwarded to Supervisor review queue.', 'success');
    }
  };

  // --- Supervisor Decision Review Approval / Rejection ---
  const handleSupervisorReview = async (decision: 'APPROVED' | 'REJECTED') => {
    if (!selectedComplaintId) return;
    if (decision === 'REJECTED' && !supervisorNotesInput.trim()) {
      setRejectionWarning(true);
      showToast('Rejection justification comment is mandatory when sending a case back!', 'error');
      return;
    }

    try {
      const response = await fetch(`/api/complaints/${selectedComplaintId}/review`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          review_decision: decision,
          supervisor_name: activeActor.name,
          supervisor_notes: supervisorNotesInput
        })
      });

      if (response.ok) {
        showToast(
          decision === 'APPROVED'
            ? 'Case approved. Payout and letter authorized.'
            : 'Case rejected. Returned back to investigator.',
          'success'
        );
        await fetchComplaints();
      } else {
        throw new Error('Supervisor review failed');
      }
    } catch (error) {
      console.warn('Supervisor review API failed, running fallback logic.', error);
      const list = complaints.map((c) => {
        if (c.id === selectedComplaintId) {
          const from_status = c.status;
          const to_status = decision === 'APPROVED' ? 'APPROVED' : 'IN_INVESTIGATION';
          
          return {
            ...c,
            status: to_status,
            review_decision: decision,
            supervisor_name: activeActor.name,
            supervisor_notes: supervisorNotesInput,
            updated_at: new Date().toISOString(),
            audit_logs: [
              ...c.audit_logs,
              {
                id: Date.now(),
                complaint_id: c.id,
                timestamp: new Date().toISOString(),
                actor_role: 'Supervisor',
                actor_name: activeActor.name,
                action_type: decision === 'APPROVED' ? 'APPROVED_BY_SUPERVISOR' : 'REJECTED_BY_SUPERVISOR',
                from_status,
                to_status,
                details:
                  decision === 'APPROVED'
                    ? `Resolution APPROVED. Notes: "${supervisorNotesInput || 'No notes left.'}"`
                    : `Resolution REJECTED and returned back to In Investigation queue. Mandatory Rejection Justification: "${supervisorNotesInput}"`
              }
            ]
          };
        }
        return c;
      });
      saveLocalState(list);
      showToast(
        decision === 'APPROVED'
          ? 'Case approved successfully (Local Sync).'
          : 'Case rejected and returned to handler (Local Sync).',
        'success'
      );
    }
  };

  // --- Add a new complaint (Intake Specialist Form submission) ---
  const handleCreateComplaint = async (formValues: Omit<Complaint, 'id' | 'reference_number' | 'status' | 'refund_amount' | 'goodwill_amount' | 'interest_amount' | 'total_redress' | 'review_decision' | 'created_at' | 'updated_at' | 'audit_logs'>) => {
    try {
      const response = await fetch('/api/complaints', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formValues)
      });

      if (response.ok) {
        showToast('Complaint recorded successfully.', 'success');
        setIsIntakeOpen(false);
        await fetchComplaints();
      } else {
        throw new Error('API Create Failed');
      }
    } catch (error) {
      console.warn('API call failed, saving complaint locally.', error);
      const nextId = complaints.length > 0 ? Math.max(...complaints.map((c) => c.id)) + 1 : 1;
      const refNumber = `CMP-2026-0${nextId}`;
      const nowStr = new Date().toISOString();

      const newComplaint: Complaint = {
        ...formValues,
        id: nextId,
        reference_number: refNumber,
        status: 'NEW',
        refund_amount: 0.0,
        goodwill_amount: 0.0,
        interest_amount: 0.0,
        total_redress: 0.0,
        review_decision: 'NONE',
        created_at: nowStr,
        updated_at: nowStr,
        audit_logs: [
          {
            id: Date.now(),
            complaint_id: nextId,
            timestamp: nowStr,
            actor_role: activeRole,
            actor_name: activeActor.name,
            action_type: 'CREATED',
            from_status: 'NONE',
            to_status: 'NEW',
            details: `Complaint created manually by Intake Specialist ${activeActor.name}. Channel: ${formValues.channel}.`
          }
        ]
      };

      const updated = [newComplaint, ...complaints];
      saveLocalState(updated);
      showToast(`Complaint registered successfully under ${refNumber}.`, 'success');
      setIsIntakeOpen(false);
    }
  };

  // --- Permissions and Interactive actions Gating based on Role ---
  const canCreateComplaint = activeRole === 'Intake Specialist' || activeRole === 'Case Handler / Investigator';
  const canInvestigate = activeRole === 'Case Handler / Investigator' || activeRole === 'Supervisor';
  const isAuditor = activeRole === 'Compliance Auditor';
  const isSupervisor = activeRole === 'Supervisor';

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col font-sans">
      
      {/* TOAST SYSTEM CONTAINER */}
      <div className="fixed top-5 right-5 z-[9999] flex flex-col gap-2.5 max-w-md w-full">
        {toasts.map((t) => (
          <div
            key={t.id}
            className={`p-4 rounded-lg shadow-xl border flex items-start gap-3 transition-all duration-300 transform translate-x-0 ${
              t.type === 'success'
                ? 'bg-emerald-950/95 border-emerald-500/30 text-emerald-200'
                : t.type === 'error'
                ? 'bg-red-950/95 border-red-500/30 text-red-200'
                : 'bg-indigo-950/95 border-indigo-500/30 text-indigo-200'
            }`}
          >
            {t.type === 'success' ? (
              <CheckCircle className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
            ) : t.type === 'error' ? (
              <ShieldAlert className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
            ) : (
              <Activity className="w-5 h-5 text-indigo-400 shrink-0 mt-0.5" />
            )}
            <div className="text-sm leading-relaxed">{t.message}</div>
          </div>
        ))}
      </div>

      {/* HEADER SECTION */}
      <header className="border-b border-slate-800 bg-slate-950/70 backdrop-blur-md sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex flex-col gap-4">
          
          {/* Main Title, logo & Role selector row */}
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            
            {/* Title & Badge */}
            <div className="flex items-center gap-3">
              <div className="bg-gradient-to-tr from-indigo-600 to-indigo-500 p-2.5 rounded-lg shadow-inner ring-1 ring-indigo-400/20">
                <Briefcase className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-lg md:text-xl font-bold tracking-tight bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent m-0">
                  Bank Complaint Resolution Workbench
                </h1>
                <p className="text-xs text-slate-400 font-medium">Internal MVP Management Platform</p>
              </div>
            </div>

            {/* Role Switcher */}
            <div className="flex flex-wrap items-center gap-2 bg-slate-900 p-1.5 rounded-xl border border-slate-800">
              <span className="text-xs text-slate-400 font-medium px-2.5">Workspace Role:</span>
              <div className="relative">
                <select
                  value={activeRole}
                  onChange={(e) => {
                    setActiveRole(e.target.value as Role);
                    showToast(`Role switched to ${e.target.value}.`, 'info');
                  }}
                  className="bg-slate-950 border border-slate-800 text-slate-200 text-xs rounded-lg px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-indigo-500 font-medium pr-8 appearance-none cursor-pointer"
                >
                  {ROLES.map((role) => (
                    <option key={role} value={role}>
                      {role}
                    </option>
                  ))}
                </select>
                <div className="absolute inset-y-0 right-2.5 flex items-center pointer-events-none text-slate-400">
                  <ArrowDown className="w-3.5 h-3.5" />
                </div>
              </div>

              {/* Active Actor Badge */}
              <div className="flex items-center gap-1.5 bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 px-2.5 py-1 rounded-lg text-[10px] font-semibold tracking-wider uppercase ml-1">
                <User className="w-3 h-3" />
                <span>{activeActor.name}</span>
              </div>

              {isAuditor && (
                <div className="flex items-center gap-1 bg-amber-500/10 text-amber-400 border border-amber-500/20 px-2 py-1 rounded-lg text-[9px] font-bold tracking-wider uppercase">
                  <Shield className="w-3 h-3 text-amber-400" />
                  <span>Read-Only Audit</span>
                </div>
              )}
            </div>

          </div>

          {/* KPI metrics bar */}
          <div className="grid grid-cols-2 md:grid-cols-6 gap-3 pt-2">
            
            {/* Total */}
            <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800/80 shadow-sm flex flex-col justify-between">
              <span className="text-[10px] text-slate-400 uppercase font-semibold tracking-wider">Total Complaints</span>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-xl md:text-2xl font-bold text-white">{stats.total}</span>
                <span className="text-[10px] text-slate-500 font-medium">cases</span>
              </div>
            </div>

            {/* In Investigation */}
            <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800/80 shadow-sm flex flex-col justify-between">
              <span className="text-[10px] text-indigo-400 uppercase font-semibold tracking-wider">In Investigation</span>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-xl md:text-2xl font-bold text-indigo-300">{stats.in_investigation}</span>
                <span className="text-[10px] text-indigo-500 font-medium">active</span>
              </div>
            </div>

            {/* Pending Review */}
            <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800/80 shadow-sm flex flex-col justify-between">
              <span className="text-[10px] text-amber-400 uppercase font-semibold tracking-wider">Pending Review</span>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-xl md:text-2xl font-bold text-amber-300">{stats.under_review}</span>
                <span className="text-[10px] text-amber-500 font-medium">queued</span>
              </div>
            </div>

            {/* Escalated */}
            <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800/80 shadow-sm flex flex-col justify-between">
              <span className="text-[10px] text-red-400 uppercase font-semibold tracking-wider">Escalated</span>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-xl md:text-2xl font-bold text-red-300">{stats.escalated}</span>
                <span className="text-[10px] text-red-500 font-medium">urgent</span>
              </div>
            </div>

            {/* Resolved */}
            <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800/80 shadow-sm flex flex-col justify-between">
              <span className="text-[10px] text-teal-400 uppercase font-semibold tracking-wider">Resolved</span>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-xl md:text-2xl font-bold text-teal-300">{stats.resolved}</span>
                <span className="text-[10px] text-teal-500 font-medium">closed</span>
              </div>
            </div>

            {/* Redress summary */}
            <div className="col-span-2 md:col-span-1 bg-indigo-950/30 p-3 rounded-xl border border-indigo-900/40 shadow-sm flex flex-col justify-between">
              <span className="text-[10px] text-indigo-300 uppercase font-semibold tracking-wider">Total Redress Paid</span>
              <div className="flex items-baseline gap-1 mt-1">
                <span className="text-xs text-indigo-400 font-medium">$</span>
                <span className="text-lg md:text-xl font-bold text-indigo-200">
                  {stats.total_redress_paid.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </span>
              </div>
            </div>

          </div>

          {/* Search, Action buttons, and Reset */}
          <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-3 pt-1 border-t border-slate-800/50">
            
            {/* Search Input bar */}
            <div className="relative flex-grow max-w-md">
              <input
                type="text"
                placeholder="Search by ID, customer name, keyword or subject..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-slate-900 border border-slate-800 rounded-xl py-2 pl-10 pr-4 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500"
              />
              <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-3 top-2 text-slate-500 hover:text-slate-300 text-xs bg-slate-800 hover:bg-slate-700 px-1.5 py-0.5 rounded"
                >
                  Clear
                </button>
              )}
            </div>

            {/* Quick action triggers */}
            <div className="flex items-center gap-2">
              
              {/* Reset seed data button */}
              <button
                onClick={handleResetData}
                disabled={loading}
                title="Reset Database to clean Synthetic State"
                className="bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 text-slate-300 text-xs px-4 py-2 rounded-xl flex items-center justify-center gap-2 cursor-pointer transition-colors disabled:opacity-50"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                <span>Reset Synthetic Data</span>
              </button>

              {/* "+ New Complaint" button - gates based on role capability */}
              <button
                onClick={() => {
                  if (!canCreateComplaint) {
                    showToast('Only Intake Specialists and Case Handlers can file new complaints.', 'error');
                    return;
                  }
                  setIsIntakeOpen(true);
                }}
                className={`text-white text-xs px-4 py-2 rounded-xl flex items-center justify-center gap-2 cursor-pointer transition-all shadow-md ${
                  canCreateComplaint
                    ? 'bg-gradient-to-tr from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 active:scale-95'
                    : 'bg-slate-800 opacity-40 cursor-not-allowed text-slate-500'
                }`}
              >
                <Plus className="w-3.5 h-3.5" />
                <span>New Complaint</span>
              </button>

            </div>

          </div>

        </div>
      </header>

      {/* FILTER TOOLBAR PANEL */}
      <section className="bg-slate-900 border-b border-slate-800/60 py-3">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-wrap items-center gap-5 text-xs">
          
          <div className="flex items-center gap-1.5 text-slate-400 font-medium">
            <Layers className="w-3.5 h-3.5 text-slate-500" />
            <span>Filters:</span>
          </div>

          {/* Priority filter */}
          <div className="flex items-center gap-2">
            <span className="text-slate-500">Priority:</span>
            <div className="flex gap-1 bg-slate-950 p-0.5 rounded-lg border border-slate-800/80">
              <button
                onClick={() => setPriorityFilter('ALL')}
                className={`px-2.5 py-1 rounded-md text-[10px] font-medium transition-colors cursor-pointer ${
                  priorityFilter === 'ALL' ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                All
              </button>
              {PRIORITIES.map((p) => (
                <button
                  key={p}
                  onClick={() => setPriorityFilter(p)}
                  className={`px-2.5 py-1 rounded-md text-[10px] font-semibold transition-colors cursor-pointer uppercase ${
                    priorityFilter === p ? 'bg-indigo-600 text-white shadow-sm' : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>

          {/* Product Filter */}
          <div className="flex items-center gap-2">
            <span className="text-slate-500">Product:</span>
            <select
              value={productFilter}
              onChange={(e) => setProductFilter(e.target.value)}
              className="bg-slate-950 border border-slate-800 text-slate-300 text-[11px] rounded-lg px-2.5 py-1 focus:outline-none"
            >
              <option value="ALL">All Products</option>
              {PRODUCTS.map((prod) => (
                <option key={prod} value={prod}>
                  {prod}
                </option>
              ))}
            </select>
          </div>

          {/* Assigned Handler Filter */}
          <div className="flex items-center gap-2">
            <span className="text-slate-500">Assigned To:</span>
            <select
              value={handlerFilter}
              onChange={(e) => setHandlerFilter(e.target.value)}
              className="bg-slate-950 border border-slate-800 text-slate-300 text-[11px] rounded-lg px-2.5 py-1 focus:outline-none"
            >
              <option value="ALL">All Staff</option>
              <option value="UNASSIGNED">Unassigned Only</option>
              {availableHandlers.map((h) => (
                <option key={h} value={h}>
                  {h}
                </option>
              ))}
            </select>
          </div>

          {/* Clear active filter indicator */}
          {(priorityFilter !== 'ALL' || productFilter !== 'ALL' || handlerFilter !== 'ALL' || searchQuery) && (
            <button
              onClick={() => {
                setPriorityFilter('ALL');
                setProductFilter('ALL');
                setHandlerFilter('ALL');
                setSearchQuery('');
                showToast('All board filters cleared.', 'info');
              }}
              className="ml-auto text-indigo-400 hover:text-indigo-300 font-semibold cursor-pointer underline decoration-indigo-400/30 underline-offset-4"
            >
              Clear All Filters
            </button>
          )}

        </div>
      </section>

      {/* BOARD SPACE SECTION */}
      <main className="flex-grow p-4 md:p-6 max-w-[1550px] mx-auto w-full overflow-x-auto">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 gap-3">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
            <span className="text-sm text-slate-400 font-medium">Synchronizing Workbench...</span>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-6 gap-4 min-w-[1250px]">
            {STAGES.map((stage) => {
              // Filters complaints in this column
              const stageComplaints = filteredComplaints.filter((c) => c.status === stage.key);
              
              return (
                <div
                  key={stage.key}
                  className="bg-slate-950/40 rounded-2xl border border-slate-800/80 p-3 flex flex-col min-h-[550px]"
                >
                  
                  {/* Column Header */}
                  <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-800/65">
                    <div className="flex items-center gap-2">
                      <span className="w-2.5 h-2.5 rounded-full bg-indigo-500 shadow-[0_0_8px_rgba(99,102,241,0.5)]"></span>
                      <span className="text-xs font-bold text-slate-200 tracking-wide">{stage.label}</span>
                    </div>
                    <span className="bg-slate-900 border border-slate-800 text-slate-400 px-2 py-0.5 rounded-md text-[10px] font-semibold tracking-wider">
                      {stageComplaints.length}
                    </span>
                  </div>

                  {/* Cards Area */}
                  <div className="flex-grow flex flex-col gap-3 overflow-y-auto max-h-[750px]">
                    {stageComplaints.length === 0 ? (
                      <div className="border border-dashed border-slate-800/60 rounded-xl py-8 px-4 flex flex-col items-center justify-center text-center">
                        <Check className="w-5 h-5 text-slate-700 mb-1" />
                        <span className="text-[10px] text-slate-600 font-medium uppercase">No Complaints</span>
                      </div>
                    ) : (
                      stageComplaints.map((c) => {
                        const sla = getSLADetails(c);
                        
                        return (
                          <div
                            key={c.id}
                            onClick={() => setSelectedComplaintId(c.id)}
                            className="bg-slate-900 hover:bg-slate-850 border border-slate-800/90 rounded-xl p-3 shadow-sm hover:shadow-lg hover:border-slate-700/80 transition-all duration-200 cursor-pointer group flex flex-col justify-between gap-3.5"
                          >
                            
                            {/* Card Header (Ref + Priority) */}
                            <div className="flex items-center justify-between">
                              <span className="text-[11px] font-bold text-slate-400 group-hover:text-indigo-400 transition-colors">
                                {c.reference_number}
                              </span>
                              
                              {/* Severity Badge */}
                              <span
                                className={`text-[9px] font-bold px-2 py-0.5 rounded-md tracking-wider border ${
                                  c.priority === 'CRITICAL'
                                    ? 'bg-red-500/10 text-red-400 border-red-500/20'
                                    : c.priority === 'HIGH'
                                    ? 'bg-orange-500/10 text-orange-400 border-orange-500/20'
                                    : c.priority === 'MEDIUM'
                                    ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20'
                                    : 'bg-slate-500/10 text-slate-400 border-slate-500/20'
                                }`}
                              >
                                {c.priority}
                              </span>
                            </div>

                            {/* Customer & Subject */}
                            <div>
                              <h3 className="text-xs font-bold text-slate-200 leading-snug line-clamp-1 group-hover:text-white transition-colors">
                                {c.subject}
                              </h3>
                              <p className="text-[11px] text-slate-400 font-medium mt-1">
                                {c.customer_name} <span className="text-slate-600">({c.account_number})</span>
                              </p>
                            </div>

                            {/* Details (Product + Disputed amount) */}
                            <div className="flex items-center justify-between pt-2 border-t border-slate-800/40 text-[10px]">
                              
                              <span className="bg-slate-950 border border-slate-800/80 text-slate-400 px-2 py-0.5 rounded font-medium">
                                {c.product_type}
                              </span>

                              {c.disputed_amount > 0 ? (
                                <span className="text-slate-300 font-bold">
                                  ${c.disputed_amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                                </span>
                              ) : (
                                <span className="text-slate-500 font-medium italic">No Dispute Amount</span>
                              )}

                            </div>

                            {/* SLA Status Pill */}
                            <div className="flex items-center justify-between text-[10px] mt-0.5 pt-1">
                              
                              <div className="flex items-center gap-1">
                                <Clock className="w-3 h-3 text-slate-500" />
                                <span className={`text-[10px] px-2 py-0.5 rounded-full border ${sla.color}`}>
                                  {sla.label}
                                </span>
                              </div>

                              {/* Redress label check */}
                              {c.total_redress > 0 && (
                                <span className="text-[10px] text-emerald-400 bg-emerald-950/40 border border-emerald-500/20 px-1.5 py-0.5 rounded-md font-semibold">
                                  +${c.total_redress.toFixed(2)} Redress
                                </span>
                              )}

                            </div>

                            {/* Assignment Status and Quick Action Footer */}
                            <div className="flex items-center justify-between pt-2.5 border-t border-slate-800/40 mt-1">
                              
                              <span className="text-[10px] font-medium text-slate-500 leading-none">
                                {c.assigned_to ? (
                                  <span className="text-slate-400 flex items-center gap-1">
                                    <User className="w-3 h-3 text-indigo-400 shrink-0" />
                                    <span className="truncate max-w-[85px]">{c.assigned_to.split(' ')[0]}</span>
                                  </span>
                                ) : (
                                  <span className="text-amber-500/80 italic font-semibold flex items-center gap-0.5">
                                    <AlertTriangle className="w-3 h-3 shrink-0" />
                                    <span>Unclaimed</span>
                                  </span>
                                )}
                              </span>

                              {/* Card Action Permitted Gated triggers */}
                              <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
                                
                                {/* Claim quick button */}
                                {!c.assigned_to && canInvestigate && (
                                  <button
                                    onClick={() => handleClaimCase(c.id)}
                                    className="bg-indigo-600 hover:bg-indigo-500 text-white text-[10px] font-bold px-2.5 py-1 rounded-md cursor-pointer transition-colors"
                                  >
                                    Claim
                                  </button>
                                )}

                                {/* Investigator Transition movements */}
                                {c.assigned_to === activeActor.name && activeRole === 'Case Handler / Investigator' && c.status === 'APPROVED' && (
                                  <button
                                    onClick={() => handleMoveStatus(c.id, 'RESOLVED')}
                                    className="bg-teal-600 hover:bg-teal-500 text-white text-[10px] font-bold px-2 py-1 rounded-md flex items-center gap-0.5 cursor-pointer transition-colors"
                                    title="Mark Case as Closed & Resolved"
                                  >
                                    <span>Resolve</span>
                                    <Check className="w-3 h-3" />
                                  </button>
                                )}

                                {/* Supervisor force moves */}
                                {isSupervisor && c.status !== 'RESOLVED' && (
                                  <button
                                    onClick={() => {
                                      const nextStageIndex = STAGES.findIndex((s) => s.key === c.status) + 1;
                                      if (nextStageIndex < STAGES.length) {
                                        handleMoveStatus(c.id, STAGES[nextStageIndex].key);
                                      }
                                    }}
                                    className="bg-slate-800 hover:bg-slate-700 text-slate-300 p-1 rounded-md cursor-pointer"
                                    title="Supervisor override: Move to next stage"
                                  >
                                    <ArrowRight className="w-3.5 h-3.5" />
                                  </button>
                                )}

                              </div>

                            </div>

                          </div>
                        );
                      })
                    )}
                  </div>

                </div>
              );
            })}
          </div>
        )}
      </main>

      {/* CASE DETAIL DRAWER */}
      {selectedComplaint && (
        <>
          {/* Background Overlay Backdrop */}
          <div
            className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-40 transition-opacity duration-300"
            onClick={() => setSelectedComplaintId(null)}
          ></div>

          {/* Drawer Panel Container */}
          <div className="fixed inset-y-0 right-0 max-w-2xl w-full bg-slate-900 border-l border-slate-800 shadow-2xl z-50 overflow-y-auto transition-transform duration-300 flex flex-col">
            
            {/* Drawer Header */}
            <div className="p-5 border-b border-slate-800 bg-slate-950/80 backdrop-blur-sm sticky top-0 z-10 flex items-center justify-between">
              
              <div className="flex items-center gap-3">
                <span className="text-sm font-bold text-slate-400 tracking-wider">
                  {selectedComplaint.reference_number}
                </span>
                
                {/* Column/Stage Tag */}
                <span className="text-[10px] font-bold px-2.5 py-1 rounded-full uppercase bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  {STAGES.find((s) => s.key === selectedComplaint.status)?.label || selectedComplaint.status}
                </span>

                {/* SLA detail badge */}
                <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${getSLADetails(selectedComplaint).color}`}>
                  {getSLADetails(selectedComplaint).label}
                </span>
              </div>

              {/* Close panel button */}
              <button
                onClick={() => setSelectedComplaintId(null)}
                className="text-slate-400 hover:text-white p-1 bg-slate-850 hover:bg-slate-800 rounded-lg cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>

            </div>

            {/* Drawer Scrollable Content */}
            <div className="p-6 flex-grow flex flex-col gap-6">

              {/* Case Subject */}
              <div>
                <h2 className="text-lg font-bold text-white tracking-tight">{selectedComplaint.subject}</h2>
                <div className="flex items-center gap-4 text-xs text-slate-400 mt-2">
                  <span className="flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5 text-slate-500" />
                    <span>Logged on {new Date(selectedComplaint.created_at).toLocaleDateString()}</span>
                  </span>
                  <span>•</span>
                  <span>Channel: {selectedComplaint.channel}</span>
                </div>
              </div>

              {/* SECTION: Customer & Account Summary Card */}
              <div className="bg-slate-950/40 rounded-xl border border-slate-800/80 p-4">
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                  <User className="w-4 h-4 text-indigo-400" />
                  <span>Customer & Account Profile</span>
                </h3>

                <div className="grid grid-cols-2 gap-4 text-xs">
                  
                  <div>
                    <span className="text-slate-500">Customer Name</span>
                    <p className="text-slate-200 font-semibold mt-0.5">{selectedComplaint.customer_name}</p>
                    <p className="text-[10px] text-slate-500 font-medium">ID: {selectedComplaint.customer_id}</p>
                  </div>

                  <div>
                    <span className="text-slate-500">Contact Details</span>
                    <p className="text-slate-300 mt-0.5 font-medium flex items-center gap-1">
                      <Mail className="w-3 h-3 text-slate-600" />
                      <span>{selectedComplaint.customer_email}</span>
                    </p>
                    <p className="text-slate-400 mt-0.5 font-medium flex items-center gap-1">
                      <Phone className="w-3 h-3 text-slate-600" />
                      <span>{selectedComplaint.customer_phone}</span>
                    </p>
                  </div>

                  <div className="pt-2.5 border-t border-slate-800/60 col-span-2 grid grid-cols-3 gap-3">
                    
                    <div>
                      <span className="text-slate-500">Account Number</span>
                      <p className="text-slate-200 font-semibold mt-0.5 flex items-center gap-1">
                        <CreditCard className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                        <span>{selectedComplaint.account_number}</span>
                      </p>
                    </div>

                    <div>
                      <span className="text-slate-500">Account Type</span>
                      <p className="text-slate-300 mt-0.5 font-medium">{selectedComplaint.account_type}</p>
                    </div>

                    <div>
                      <span className="text-slate-500">Disputed Amount</span>
                      <p className="text-slate-200 font-bold mt-0.5 text-indigo-400">
                        ${selectedComplaint.disputed_amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                      </p>
                    </div>

                  </div>

                </div>
              </div>

              {/* SECTION: Disputed Narrative text */}
              <div className="bg-slate-950/20 p-4 rounded-xl border border-slate-800/40">
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-2">
                  <FileText className="w-4 h-4 text-indigo-400" />
                  <span>Grievance Narrative / Narrative Description</span>
                </h3>
                <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/60 p-3.5 rounded-lg border border-slate-950">
                  "{selectedComplaint.narrative}"
                </p>
              </div>

              {/* SECTION: Investigation Findings Editor */}
              <div className="bg-slate-950/40 rounded-xl border border-slate-800/80 p-4">
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3.5 flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <Activity className="w-4 h-4 text-indigo-400" />
                    <span>Investigation Findings & Root Cause Taxonomy</span>
                  </span>
                  
                  {/* Status Indicator */}
                  {selectedComplaint.root_cause ? (
                    <span className="text-[10px] text-emerald-400 bg-emerald-950/30 px-2 py-0.5 rounded font-semibold border border-emerald-500/10">
                      Logged
                    </span>
                  ) : (
                    <span className="text-[10px] text-amber-500 bg-amber-950/30 px-2 py-0.5 rounded font-semibold border border-amber-500/10">
                      Action Required
                    </span>
                  )}
                </h3>

                {/* Form fields active based on permission */}
                {canInvestigate && selectedComplaint.status !== 'RESOLVED' ? (
                  <div className="flex flex-col gap-4 text-xs">
                    
                    {/* Root Cause Dropdown */}
                    <div>
                      <label className="text-slate-400 block mb-1.5 font-medium">Root Cause Taxonomy *</label>
                      <select
                        value={rootCauseInput}
                        onChange={(e) => setRootCauseInput(e.target.value)}
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs focus:outline-none focus:ring-1 focus:ring-indigo-500"
                      >
                        <option value="">-- Select Root Cause Reason --</option>
                        {ROOT_CAUSES.map((rc) => (
                          <option key={rc} value={rc}>
                            {rc}
                          </option>
                        ))}
                      </select>
                    </div>

                    {/* Findings textarea */}
                    <div>
                      <label className="text-slate-400 block mb-1.5 font-medium">Investigation / Diagnostics Notes *</label>
                      <textarea
                        value={notesInput}
                        onChange={(e) => setInvestigationNotesInput(e.target.value)}
                        rows={3}
                        placeholder="Detail system checks, conversations, branch communications, policy matches, and diagnostic outcomes..."
                        className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                      />
                    </div>

                    {/* Action trigger button */}
                    <button
                      type="button"
                      onClick={handleSaveFindings}
                      className="bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white px-4 py-2 rounded-lg cursor-pointer flex items-center justify-center gap-2 self-end font-semibold border border-slate-750 transition-colors"
                    >
                      <Save className="w-3.5 h-3.5" />
                      <span>Save Findings</span>
                    </button>

                  </div>
                ) : (
                  // Read-Only view of Findings
                  <div className="text-xs flex flex-col gap-3">
                    <div>
                      <span className="text-slate-500">Root Cause Taxonomy</span>
                      <p className="text-slate-200 font-semibold mt-0.5 bg-slate-950 px-2 py-1.5 rounded-lg border border-slate-800">
                        {selectedComplaint.root_cause || <span className="text-slate-600 italic">Unspecified</span>}
                      </p>
                    </div>
                    <div>
                      <span className="text-slate-500">Investigation Notes</span>
                      <p className="text-slate-300 mt-1 bg-slate-950/80 p-3 rounded-lg border border-slate-900 leading-relaxed whitespace-pre-wrap italic text-[11px]">
                        {selectedComplaint.investigation_notes || <span className="text-slate-600 italic">No notes captured yet.</span>}
                      </p>
                    </div>
                  </div>
                )}
              </div>

              {/* SECTION: Redress Calculator */}
              <div className="bg-slate-950/40 rounded-xl border border-slate-800/80 p-4">
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3.5 flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-indigo-400" />
                    <span>Redress Calculator (Financial Restitution)</span>
                  </span>

                  {selectedComplaint.total_redress > 0 && (
                    <span className="text-[10px] text-emerald-400 bg-emerald-950/30 px-2 py-0.5 rounded font-bold border border-emerald-500/10">
                      Calculated
                    </span>
                  )}
                </h3>

                {canInvestigate && selectedComplaint.status !== 'RESOLVED' ? (
                  <div className="flex flex-col gap-4 text-xs">
                    
                    <div className="grid grid-cols-3 gap-3">
                      
                      {/* Refund amount input */}
                      <div>
                        <label className="text-slate-400 block mb-1 font-medium">Refund ($) *</label>
                        <input
                          type="number"
                          step="0.01"
                          min="0"
                          value={refundInput}
                          onChange={(e) => setRefundInput(e.target.value)}
                          placeholder="0.00"
                          className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs focus:outline-none"
                        />
                      </div>

                      {/* Goodwill Compensation input */}
                      <div>
                        <label className="text-slate-400 block mb-1 font-medium">Goodwill ($)</label>
                        <input
                          type="number"
                          step="0.01"
                          min="0"
                          value={goodwillInput}
                          onChange={(e) => setGoodwillInput(e.target.value)}
                          placeholder="0.00"
                          className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs focus:outline-none"
                        />
                      </div>

                      {/* Interest Correction input */}
                      <div>
                        <label className="text-slate-400 block mb-1 font-medium">Interest ($)</label>
                        <input
                          type="number"
                          step="0.01"
                          min="0"
                          value={interestInput}
                          onChange={(e) => setInterestInput(e.target.value)}
                          placeholder="0.00"
                          className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs focus:outline-none"
                        />
                      </div>

                    </div>

                    {/* Reactive Live Sum Display */}
                    <div className="bg-slate-950 p-3 rounded-xl border border-slate-850 flex items-center justify-between">
                      <div className="flex items-center gap-1.5">
                        <CheckCircle className="w-4 h-4 text-emerald-400" />
                        <span className="text-slate-400 font-semibold uppercase tracking-wider text-[10px]">Live Total Redress</span>
                      </div>
                      <span className="text-sm font-black text-emerald-400">${liveTotalRedress.toFixed(2)}</span>
                    </div>

                    {/* Action buttons */}
                    <button
                      type="button"
                      onClick={handleSaveRedress}
                      className="bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white px-4 py-2 rounded-lg cursor-pointer flex items-center justify-center gap-2 self-end font-semibold border border-slate-750 transition-colors"
                    >
                      <Save className="w-3.5 h-3.5" />
                      <span>Save Redress</span>
                    </button>

                  </div>
                ) : (
                  // Read-Only view of Redress Calculator
                  <div className="grid grid-cols-4 gap-3 text-xs bg-slate-950 p-3 rounded-lg border border-slate-900 text-center">
                    <div>
                      <span className="text-slate-500">Refund</span>
                      <p className="text-slate-200 font-semibold mt-1">${selectedComplaint.refund_amount.toFixed(2)}</p>
                    </div>
                    <div>
                      <span className="text-slate-500">Goodwill</span>
                      <p className="text-slate-200 font-semibold mt-1">${selectedComplaint.goodwill_amount.toFixed(2)}</p>
                    </div>
                    <div>
                      <span className="text-slate-500">Interest</span>
                      <p className="text-slate-200 font-semibold mt-1">${selectedComplaint.interest_amount.toFixed(2)}</p>
                    </div>
                    <div className="bg-emerald-950/20 px-2 py-1 rounded border border-emerald-500/10">
                      <span className="text-emerald-400 font-semibold">Total</span>
                      <p className="text-emerald-300 font-bold mt-1">${selectedComplaint.total_redress.toFixed(2)}</p>
                    </div>
                  </div>
                )}
              </div>

              {/* ACTION: Submit to Supervisor for Review */}
              {selectedComplaint.status === 'IN_INVESTIGATION' && canInvestigate && (
                <div className="bg-indigo-950/30 border border-indigo-500/30 rounded-xl p-4 flex flex-col gap-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <ShieldAlert className="w-4 h-4 text-indigo-400" />
                      <h4 className="text-xs font-bold text-indigo-300 uppercase tracking-wider">Submit for Supervisor Approval</h4>
                    </div>
                  </div>
                  <p className="text-[11px] text-slate-400">
                    Once root cause findings and financial redress are saved, escalate this case to supervisor review.
                  </p>
                  <button
                    type="button"
                    onClick={handleSubmitForReview}
                    className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs py-2 px-4 rounded-lg cursor-pointer flex items-center justify-center gap-2 transition-colors self-end"
                  >
                    <ArrowRight className="w-4 h-4" />
                    <span>Submit for Review</span>
                  </button>
                </div>
              )}

              {/* SUPERVISOR SIGN-OFF & RETURN PANEL */}
              {selectedComplaint.status === 'UNDER_REVIEW' && (
                <div className="bg-gradient-to-tr from-amber-950/20 to-slate-900 border-2 border-dashed border-amber-500/30 rounded-2xl p-5 shadow-inner">
                  
                  <div className="flex items-start gap-3">
                    <Shield className="w-6 h-6 text-amber-500 shrink-0 mt-0.5" />
                    <div>
                      <h3 className="text-xs font-black text-amber-400 uppercase tracking-widest">Supervisor Sign-Off Panel</h3>
                      <p className="text-[10px] text-slate-400 mt-1 leading-relaxed">
                        Verify the root cause taxonomy and proposed redress calculations. You can either sign-off and approve, or return with notes.
                      </p>
                    </div>
                  </div>

                  {isSupervisor ? (
                    <div className="mt-4 flex flex-col gap-4 text-xs">
                      
                      {/* Review feedback textarea */}
                      <div>
                        <label className="text-slate-300 block mb-1 font-semibold">Supervisor Feedback Notes</label>
                        <textarea
                          value={supervisorNotesInput}
                          onChange={(e) => {
                            setSupervisorNotesInput(e.target.value);
                            if (e.target.value.trim()) setRejectionWarning(false);
                          }}
                          placeholder={
                            rejectionWarning
                              ? '⚠️ REJECTION NOTES ARE MANDATORY! Please explain what needs to be changed...'
                              : 'Log supervisor oversight checks, details of validation, or feedback for the handler...'
                          }
                          rows={3.5}
                          className={`w-full bg-slate-950 border rounded-lg p-2.5 text-xs text-slate-200 focus:outline-none transition-colors ${
                            rejectionWarning ? 'border-red-500/60 placeholder-red-400/60' : 'border-slate-800 focus:ring-1 focus:ring-amber-500'
                          }`}
                        />
                      </div>

                      {/* Sign-Off Action Triggers */}
                      <div className="flex gap-2 justify-end">
                        
                        {/* Reject and send back button */}
                        <button
                          type="button"
                          onClick={() => handleSupervisorReview('REJECTED')}
                          className="bg-red-950 hover:bg-red-900 text-red-200 hover:text-white px-4 py-2.5 rounded-xl cursor-pointer flex items-center gap-1.5 font-bold transition-colors border border-red-500/20"
                          title="Reject resolution and send back to In Investigation stage"
                        >
                          <Ban className="w-3.5 h-3.5" />
                          <span>Reject & Return</span>
                        </button>

                        {/* Approve button */}
                        <button
                          type="button"
                          onClick={() => handleSupervisorReview('APPROVED')}
                          className="bg-gradient-to-tr from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 text-white px-5 py-2.5 rounded-xl cursor-pointer flex items-center gap-1.5 font-bold transition-all shadow-md active:scale-95"
                          title="Approve case redress and authorize settlement status"
                        >
                          <Check className="w-3.5 h-3.5" />
                          <span>Approve Resolution</span>
                        </button>

                      </div>

                    </div>
                  ) : (
                    // Read only warning of locked supervisor section
                    <div className="mt-3 bg-slate-950/60 p-3 rounded-lg border border-slate-950 flex items-center gap-2.5 text-[10px] text-slate-400 italic">
                      <Lock className="w-4 h-4 text-slate-500 shrink-0" />
                      <span>Review operations are gated. Switch to the "Supervisor" workspace role to authorize decisions.</span>
                    </div>
                  )}

                </div>
              )}

              {/* ACTION: Investigator Closing Settlement / Re-assignment Option */}
              {selectedComplaint.status === 'APPROVED' && activeRole === 'Case Handler / Investigator' && selectedComplaint.assigned_to === activeActor.name && (
                <div className="bg-indigo-950/20 border border-indigo-500/30 rounded-xl p-4 flex flex-col gap-3">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="w-5 h-5 text-indigo-400" />
                    <h3 className="text-xs font-bold text-indigo-300 uppercase tracking-wider">Final Customer Settlement</h3>
                  </div>
                  <p className="text-[11px] text-slate-400">
                    The redress has been officially signed off by a Supervisor. Disburse the payment and close this complaint.
                  </p>
                  <button
                    onClick={() => handleMoveStatus(selectedComplaint.id, 'RESOLVED')}
                    className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs py-2 px-4 rounded-lg cursor-pointer transition-colors"
                  >
                    Authorize payout & close case file
                  </button>
                </div>
              )}

              {/* ACTION: Self Assignment / Claim if unassigned */}
              {!selectedComplaint.assigned_to && canInvestigate && (
                <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800 flex flex-col gap-3">
                  <span className="text-xs font-bold text-slate-400">Claim This Case</span>
                  <p className="text-[11px] text-slate-500">Take responsibility for this customer. Claiming will assign you as the case handler and move it to investigation.</p>
                  <button
                    onClick={() => handleClaimCase(selectedComplaint.id)}
                    className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs py-2 rounded-lg cursor-pointer"
                  >
                    Claim complaint file
                  </button>
                </div>
              )}

              {/* AUDIT LOG TIMELINE */}
              <div className="border-t border-slate-800 pt-6">
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                  <Activity className="w-4 h-4 text-indigo-400" />
                  <span>Immutable Case Audit History</span>
                </h3>

                {selectedComplaint.audit_logs.length === 0 ? (
                  <p className="text-xs text-slate-500 italic">No audit records found.</p>
                ) : (
                  <div className="relative pl-6 border-l-2 border-slate-800 flex flex-col gap-6 ml-2.5">
                    {selectedComplaint.audit_logs.map((log) => {
                      // Custom timeline node colors based on action
                      const isCreated = log.action_type === 'CREATED';
                      const isApproved = log.action_type === 'APPROVED_BY_SUPERVISOR' || log.to_status === 'APPROVED';
                      const isRejected = log.action_type === 'REJECTED_BY_SUPERVISOR';
                      const isResolved = log.to_status === 'RESOLVED';

                      return (
                        <div key={log.id} className="relative group text-xs">
                          
                          {/* Timeline dot badge */}
                          <span
                            className={`absolute -left-[31px] top-1 w-4 h-4 rounded-full border-2 bg-slate-900 transition-transform duration-200 group-hover:scale-125 ${
                              isCreated
                                ? 'border-blue-500 shadow-[0_0_8px_rgba(59,130,246,0.3)]'
                                : isApproved
                                ? 'border-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.3)]'
                                : isRejected
                                ? 'border-red-500 shadow-[0_0_8px_rgba(239,68,68,0.3)]'
                                : isResolved
                                ? 'border-teal-500'
                                : 'border-indigo-400'
                            }`}
                          ></span>

                          {/* Timestamp and Actor Role */}
                          <div className="flex items-center justify-between text-[10px] text-slate-500 font-medium">
                            <span>{new Date(log.timestamp).toLocaleString()}</span>
                            <span className="bg-slate-950 border border-slate-850 px-2 py-0.5 rounded uppercase tracking-wider text-[8px] font-bold">
                              {log.actor_role}
                            </span>
                          </div>

                          {/* Detail summary */}
                          <p className="text-slate-300 font-semibold mt-1">
                            {log.details || `Status changed to ${log.to_status}.`}
                          </p>

                          {/* Actor name signature */}
                          <div className="text-[10px] text-slate-400 mt-0.5 font-medium flex items-center gap-1">
                            <span className="text-slate-600">By</span>
                            <span>{log.actor_name}</span>
                          </div>

                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

            </div>

          </div>
        </>
      )}

      {/* CASE INTAKE MODAL */}
      {isIntakeOpen && (
        <IntakeModal
          onClose={() => setIsIntakeOpen(false)}
          onSubmit={handleCreateComplaint}
          activeActorName={activeActor.name}
          activeRoleName={activeRole}
          showToast={showToast}
        />
      )}

      {/* PLATFORM CONVENTIONS FOOTER */}
      <footer className="bg-slate-950 border-t border-slate-800 py-6 mt-auto text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center flex flex-col md:flex-row items-center justify-between gap-3">
          <p>© 2026 Synthetic Banking Group. Internal Audit System.</p>
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1">
              <Shield className="w-3.5 h-3.5 text-indigo-400" />
              <span>Immutable Audits Enabled</span>
            </span>
            <span>•</span>
            <span className="text-indigo-400 font-semibold">Strict Role Permission Gating Active</span>
          </div>
        </div>
      </footer>

    </div>
  );
}

// --- CASE INTAKE MODAL SUBCOMPONENT ---
interface IntakeModalProps {
  onClose: () => void;
  onSubmit: (formValues: any) => Promise<void>;
  activeActorName: string;
  activeRoleName: string;
  showToast: (msg: string, type: any) => void;
}

function IntakeModal({ onClose, onSubmit, activeActorName, activeRoleName, showToast }: IntakeModalProps) {
  // Field values
  const [customerName, setCustomerName] = useState('');
  const [customerId, setCustomerId] = useState('');
  const [customerEmail, setCustomerEmail] = useState('');
  const [customerPhone, setCustomerPhone] = useState('');
  const [accountNumber, setAccountNumber] = useState('');
  const [accountType, setAccountType] = useState('Checking');
  const [productType, setProductType] = useState('Checking');
  const [category, setCategory] = useState('Unauthorized Transaction');
  const [priority, setPriority] = useState('MEDIUM');
  const [channel, setChannel] = useState('Online Banking');
  const [subject, setSubject] = useState('');
  const [narrative, setNarrative] = useState('');
  const [disputedAmount, setDisputedAmount] = useState('');

  // Auto populate synthetic mock profile button
  const handleLoadSyntheticProfile = () => {
    const list = [
      { name: 'Sarah Jenkins', email: 's.jenkins@gmail.synthetic.com', phone: '+1 (555) 019-3841', act: 'Checking', num: 'ACCT-8891-032' },
      { name: 'David Vance', email: 'vance.d@corp.synthetic.com', phone: '+1 (555) 012-4412', act: 'Business Account', num: 'ACCT-3912-990' },
      { name: 'Marcus Aurelius', email: 'marcus.rome@emperor.synthetic.com', phone: '+1 (555) 015-8831', act: 'Mortgage', num: 'ACCT-1122-384' },
      { name: 'Eleanor Vance', email: 'e.vance@vance.synthetic.com', phone: '+1 (555) 013-1182', act: 'Credit Card', num: 'CARD-9012-384' }
    ];
    const item = list[Math.floor(Math.random() * list.length)];
    setCustomerName(item.name);
    setCustomerId(`CUST-${Math.floor(1000 + Math.random() * 9000)}`);
    setCustomerEmail(item.email);
    setCustomerPhone(item.phone);
    setAccountNumber(item.num);
    setAccountType(item.act);
    setProductType(item.act === 'Business Account' ? 'Wire Transfer' : item.act === 'Credit Card' ? 'Credit Card' : 'Checking');
    showToast('Synthetic customer identity loaded.', 'info');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!customerName || !customerId || !customerEmail || !accountNumber || !subject || !narrative) {
      showToast('All fields marked * are required.', 'error');
      return;
    }
    // Simple email validation
    if (!customerEmail.includes('@') || !customerEmail.includes('.')) {
      showToast('Please enter a valid synthetic email.', 'error');
      return;
    }

    const amt = parseFloat(disputedAmount);
    if (isNaN(amt) || amt < 0) {
      showToast('Disputed amount must be a positive number (enter 0 for service complaints).', 'error');
      return;
    }

    onSubmit({
      customer_name: customerName,
      customer_id: customerId,
      customer_email: customerEmail,
      customer_phone: customerPhone || '+1 (555) 010-0000',
      account_number: accountNumber,
      account_type: accountType,
      product_type: productType,
      category,
      priority,
      channel,
      subject,
      narrative,
      disputed_amount: amt,
      sla_target_hours: 168
    });
  };

  return (
    <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-2xl w-full shadow-2xl overflow-hidden flex flex-col max-h-[90vh]">
        
        {/* Modal Header */}
        <div className="p-5 border-b border-slate-800 bg-slate-950/40 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <UserPlus className="w-5 h-5 text-indigo-400" />
            <h2 className="text-base font-bold text-white m-0">Record New Complaint (Case Intake)</h2>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white p-1 rounded bg-slate-800 hover:bg-slate-700 cursor-pointer">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Scrollable Form */}
        <form onSubmit={handleSubmit} className="p-6 overflow-y-auto flex-grow flex flex-col gap-5 text-xs">
          
          {/* Quick populate tool */}
          <div className="bg-indigo-950/20 border border-indigo-500/20 p-3 rounded-xl flex items-center justify-between">
            <div>
              <span className="font-bold text-indigo-300">Intake synthetic identity generator</span>
              <p className="text-[10px] text-slate-400">Instantly generate a realistic synthetic bank customer.</p>
            </div>
            <button
              type="button"
              onClick={handleLoadSyntheticProfile}
              className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-1 px-3 rounded-lg text-[10px] cursor-pointer"
            >
              Autofill Profile
            </button>
          </div>

          {/* Section: Customer Profile */}
          <div>
            <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-3 pb-1 border-b border-slate-800">
              1. Customer Synthetic Profile
            </h3>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-slate-400 block mb-1">Customer Name *</label>
                <input
                  type="text"
                  value={customerName}
                  onChange={(e) => setCustomerName(e.target.value)}
                  placeholder="e.g. Sarah Connor"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 focus:outline-none"
                  required
                />
              </div>
              <div>
                <label className="text-slate-400 block mb-1">Customer ID *</label>
                <input
                  type="text"
                  value={customerId}
                  onChange={(e) => setCustomerId(e.target.value)}
                  placeholder="e.g. CUST-4912"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 focus:outline-none"
                  required
                />
              </div>
              <div>
                <label className="text-slate-400 block mb-1">Synthetic Email *</label>
                <input
                  type="email"
                  value={customerEmail}
                  onChange={(e) => setCustomerEmail(e.target.value)}
                  placeholder="e.g. sarah.c@synthetic.bank.com"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 focus:outline-none"
                  required
                />
              </div>
              <div>
                <label className="text-slate-400 block mb-1">Synthetic Phone</label>
                <input
                  type="text"
                  value={customerPhone}
                  onChange={(e) => setCustomerPhone(e.target.value)}
                  placeholder="e.g. +1 (555) 012-4859"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 focus:outline-none"
                />
              </div>
            </div>
          </div>

          {/* Section: Account & Product */}
          <div>
            <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-3 pb-1 border-b border-slate-800">
              2. Account & Financial Metadata
            </h3>
            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="text-slate-400 block mb-1">Account Number *</label>
                <input
                  type="text"
                  value={accountNumber}
                  onChange={(e) => setAccountNumber(e.target.value)}
                  placeholder="e.g. ACCT-1102-392"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 focus:outline-none"
                  required
                />
              </div>
              <div>
                <label className="text-slate-400 block mb-1">Account Type *</label>
                <select
                  value={accountType}
                  onChange={(e) => setAccountType(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 focus:outline-none"
                >
                  {ACCOUNT_TYPES.map((a) => (
                    <option key={a} value={a}>
                      {a}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-slate-400 block mb-1">Product Type *</label>
                <select
                  value={productType}
                  onChange={(e) => setProductType(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 focus:outline-none"
                >
                  {PRODUCTS.map((p) => (
                    <option key={p} value={p}>
                      {p}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Section: Complaint Details */}
          <div>
            <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-3 pb-1 border-b border-slate-800">
              3. Grievance Content & Metadata
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
              <div>
                <label className="text-slate-400 block mb-1">Category *</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 focus:outline-none"
                >
                  {CATEGORIES.map((cat) => (
                    <option key={cat} value={cat}>
                      {cat}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-slate-400 block mb-1">Priority *</label>
                <select
                  value={priority}
                  onChange={(e) => setPriority(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 focus:outline-none"
                >
                  {PRIORITIES.map((p) => (
                    <option key={p} value={p}>
                      {p}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-slate-400 block mb-1">Channel *</label>
                <select
                  value={channel}
                  onChange={(e) => setChannel(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 focus:outline-none"
                >
                  {CHANNELS.map((ch) => (
                    <option key={ch} value={ch}>
                      {ch}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-slate-400 block mb-1">Disputed Amount ($) *</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  value={disputedAmount}
                  onChange={(e) => setDisputedAmount(e.target.value)}
                  placeholder="0.00"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 focus:outline-none"
                  required
                />
              </div>
            </div>

            <div className="flex flex-col gap-3">
              <div>
                <label className="text-slate-400 block mb-1">Grievance Subject / Title *</label>
                <input
                  type="text"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  placeholder="e.g. Double ATM Fee Charge on Statement"
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 focus:outline-none"
                  required
                />
              </div>
              <div>
                <label className="text-slate-400 block mb-1">Narrative Description / Narrative *</label>
                <textarea
                  value={narrative}
                  onChange={(e) => setNarrative(e.target.value)}
                  rows={4}
                  placeholder="Enter full transcript of the customer's explanation. Include chronological events, transaction amounts, staff interactions, and customer's specific request for resolution..."
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-slate-200 placeholder-slate-600 focus:outline-none"
                  required
                />
              </div>
            </div>
          </div>

          {/* Form Actions Footer */}
          <div className="flex items-center justify-between pt-4 border-t border-slate-800 bg-slate-950/20 mt-1">
            <span className="text-[10px] text-slate-500 italic">
              Logged by: {activeActorName} ({activeRoleName})
            </span>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={onClose}
                className="bg-slate-800 hover:bg-slate-700 text-slate-300 font-semibold py-2 px-4 rounded-xl cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-2 px-5 rounded-xl cursor-pointer shadow-md transition-all active:scale-95"
              >
                File Complaint File
              </button>
            </div>
          </div>

        </form>

      </div>
    </div>
  );
}
