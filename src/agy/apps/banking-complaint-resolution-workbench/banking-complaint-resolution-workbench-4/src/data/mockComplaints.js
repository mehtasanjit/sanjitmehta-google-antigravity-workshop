export const mockComplaintsData = [
  {
    id: "CMP-2026-9042",
    customerName: "Eleanor Vance",
    accountNumber: "ACC-882190-01",
    customerTier: "Private Client",
    email: "eleanor.vance@vanceholdings.com",
    phone: "+1 (555) 234-8901",
    customerTenure: "8 years",
    customerRiskScore: "Low (12/100)",
    accountBalance: "$142,500.00",
    title: "Unauthorized International Wire Transfer of $12,450 to Overseas Account",
    product: "Wire Transfers",
    channel: "CFPB Portal",
    priority: "Critical",
    status: "Under Investigation",
    disputedAmount: 12450.00,
    regulatoryTag: "CFPB Expedited & Reg E",
    rootCause: "Suspected Account Takeover (ATO) / SIM Swap",
    assignedTo: "Marcus Chen (Lead Fraud Analyst)",
    createdAt: "2026-08-20T08:15:00Z",
    slaDeadline: "2026-08-21T18:00:00Z", // Approaching SLA
    sentiment: "Highly Frustrated / Threatening Legal Action",
    narrative: "Customer reports that an unauthorized international wire transfer of $12,450.00 was executed from her commercial checking account yesterday morning to an unknown beneficiary bank in Cyprus. Customer states she was traveling abroad and experienced cellular network disruption (likely SIM swap). She never authorized two-factor verification codes and contacted the priority emergency fraud line within 2 hours of noticing the debit. She demands immediate provisional credit and a full recall request.",
    timeline: [
      {
        id: "ev-1",
        timestamp: "2026-08-20T08:15:00Z",
        type: "complaint_filed",
        author: "CFPB Intake Portal",
        content: "Complaint forwarded from CFPB Portal with expedited 15-day resolution mandate."
      },
      {
        id: "ev-2",
        timestamp: "2026-08-20T09:30:00Z",
        type: "agent_note",
        author: "Marcus Chen",
        content: "Initiated SWIFT gpi wire recall (GPI Ref: REC-994012) to intermediary bank. Flagged IP login origin (Larnaca, Cyprus via VPN)."
      },
      {
        id: "ev-3",
        timestamp: "2026-08-20T14:20:00Z",
        type: "system_event",
        author: "Fraud Detection Engine",
        content: "Device fingerprint mismatch detected. 2FA push notification acknowledged on unknown iOS 19.1 device."
      }
    ],
    recommendedRemediation: {
      action: "Issue Provisional Credit & Freeze Beneficiary Wire",
      amount: 12450.00,
      regulationBasis: "Regulation E § 1005.11(c) requires provisional credit within 10 business days for consumer accounts; under Private Client Service Agreement, expedited 24-hour credit is standard."
    }
  },
  {
    id: "CMP-2026-8941",
    customerName: "David Sterling",
    accountNumber: "ACC-541209-88",
    customerTier: "Preferred",
    email: "david.sterling@sterlingarch.com",
    phone: "+1 (555) 789-4321",
    customerTenure: "5 years",
    customerRiskScore: "Low (24/100)",
    accountBalance: "$34,200.00",
    title: "Double Charged on Merchant Terminal with Refusal of Refund",
    product: "Credit Cards",
    channel: "Mobile App",
    priority: "High",
    status: "Under Investigation",
    disputedAmount: 1850.00,
    regulatoryTag: "Regulation Z (Truth in Lending)",
    rootCause: "POS Settlement Duplicate Batch",
    assignedTo: "Sarah Jenkins",
    createdAt: "2026-08-19T11:45:00Z",
    slaDeadline: "2026-08-22T17:00:00Z",
    sentiment: "Upset / Disappointed",
    narrative: "Customer attempted to purchase airline tickets ($1,850.00) on his Apex Signature Visa. The terminal threw a communication error, so the merchant ran it a second time. Both transactions posted and settled to his statement. Merchant customer service refused to void the duplicate, insisting Apex Bank must handle the dispute.",
    timeline: [
      {
        id: "ev-10",
        timestamp: "2026-08-19T11:45:00Z",
        type: "complaint_filed",
        author: "David Sterling (via Mobile App)",
        content: "Dispute submitted with attached receipts showing identical transaction timestamps (11:42:01 and 11:42:18)."
      },
      {
        id: "ev-11",
        timestamp: "2026-08-19T16:00:00Z",
        type: "agent_note",
        author: "Sarah Jenkins",
        content: "Verified batch capture IDs. Both transactions share ARN #884910294. Chargeback Reason Code 4834 (Duplicate Processing) initiated via Visa Resolve."
      }
    ],
    recommendedRemediation: {
      action: "Immediate Chargeback Filing & Temporary Statement Credit",
      amount: 1850.00,
      regulationBasis: "Regulation Z 12 CFR § 1026.13 - Billing error resolution guidelines."
    }
  },
  {
    id: "CMP-2026-8790",
    customerName: "Maria Rodriguez-Santos",
    accountNumber: "ACC-331902-12",
    customerTier: "Standard",
    email: "m.rodriguez@gmail.com",
    phone: "+1 (555) 902-1847",
    customerTenure: "3 years",
    customerRiskScore: "Medium (45/100)",
    accountBalance: "$890.50",
    title: "Excessive Cascade of Overdraft Fees Caused by Delayed Direct Deposit Posting",
    product: "Checking & Savings",
    channel: "Branch",
    priority: "Medium",
    status: "New",
    disputedAmount: 210.00,
    regulatoryTag: "CFPB Unfair Practice Review",
    rootCause: "ACH Processing Window Lag",
    assignedTo: "Unassigned",
    createdAt: "2026-08-21T06:30:00Z",
    slaDeadline: "2026-08-23T12:00:00Z",
    sentiment: "Anxious / Frustrated",
    narrative: "Customer's payroll direct deposit was delayed by 6 hours due to a clearing house transmission delay on Friday. During this window, six small automated debits ($12, $8.50, $15, $22, $31, $40) hit the account, each incurring a $35 overdraft fee totaling $210.00. Customer visited the Downtown branch and was told branch staff could only waive two fees per policy.",
    timeline: [
      {
        id: "ev-20",
        timestamp: "2026-08-21T06:30:00Z",
        type: "complaint_filed",
        author: "Downtown Branch Staff #402",
        content: "Escalated from branch intake desk following customer dispute over branch fee waiver cap."
      }
    ],
    recommendedRemediation: {
      action: "Full Fee Waiver (6 x $35 = $210) as Courtesy / System Lag Exception",
      amount: 210.00,
      regulationBasis: "CFPB Policy Statement on abusive resequencing and deposit posting delays."
    }
  },
  {
    id: "CMP-2026-8610",
    customerName: "Apex Logistics LLC (Rep: Thomas Hayes)",
    accountNumber: "ACC-901188-44",
    customerTier: "Commercial",
    email: "thayes@apexlogistics.io",
    phone: "+1 (555) 661-9000",
    customerTenure: "7 years",
    customerRiskScore: "Low (18/100)",
    accountBalance: "$580,000.00",
    title: "Commercial Payroll Account Sudden Freeze without Advance Notification",
    product: "Commercial Banking",
    channel: "Phone",
    priority: "Critical",
    status: "Escalated",
    disputedAmount: 0.00,
    regulatoryTag: "Executive Escalation",
    rootCause: "Automated AML Rule False Positive",
    assignedTo: "Elena Rostova (VP Ops & Compliance)",
    createdAt: "2026-08-20T16:00:00Z",
    slaDeadline: "2026-08-21T10:00:00Z", // BREACHED / URGENT
    sentiment: "Extremely Angry / Threatening Business Closure Lawsuit",
    narrative: "Commercial client with 85 employees had their primary disbursement account automatically locked at 3:30 PM due to a sudden volume spike from quarterly bonus payments. Payroll batch for tomorrow morning ($310,000) was halted. Client has already contacted corporate counsel and regional managing director.",
    timeline: [
      {
        id: "ev-30",
        timestamp: "2026-08-20T16:00:00Z",
        type: "complaint_filed",
        author: "Phone Rep #118",
        content: "High-priority corporate escalation. Client CEO on the line with Relationship Manager."
      },
      {
        id: "ev-31",
        timestamp: "2026-08-20T17:15:00Z",
        type: "agent_note",
        author: "Elena Rostova",
        content: "Reviewed AML trigger. Alert tripped on 'Out of Pattern Batch Size'. Verified corporate tax filings and board bonus resolution."
      }
    ],
    recommendedRemediation: {
      action: "Immediate Manual Unfreeze, AML False Positive Whitelist & Executive Apology Letter",
      amount: 0.00,
      regulationBasis: "Commercial Client Service Level Agreement & BSA/AML Risk-Based Policy § 4.2."
    }
  },
  {
    id: "CMP-2026-8502",
    customerName: "Kendra Washington",
    accountNumber: "ACC-190284-91",
    customerTier: "Preferred",
    email: "kendra.w@seattlehealth.org",
    phone: "+1 (555) 441-2091",
    customerTenure: "4 years",
    customerRiskScore: "Low (8/100)",
    accountBalance: "$22,400.00",
    title: "Incorrect 30-Day Late Mark Reported to Experian & Equifax During Auto-Pay Transition",
    product: "Mortgages & Loans",
    channel: "CFPB Portal",
    priority: "High",
    status: "Under Investigation",
    disputedAmount: 0.00,
    regulatoryTag: "FCRA (Fair Credit Reporting Act)",
    rootCause: "Core Banking Migration Data Glitch",
    assignedTo: "Marcus Chen (Lead Fraud Analyst)",
    createdAt: "2026-08-18T09:00:00Z",
    slaDeadline: "2026-08-24T18:00:00Z",
    sentiment: "Distressed / Seeking Mortgage Refinance",
    narrative: "During the core loan servicing platform upgrade in June, customer's scheduled auto-debit was skipped by the system. The loan system marked the payment delinquent and automatically reported a 30-day late payment to Equifax, Experian, and TransUnion. Customer's credit score dropped 78 points, impacting her current rate-lock on an investment property purchase.",
    timeline: [
      {
        id: "ev-40",
        timestamp: "2026-08-18T09:00:00Z",
        type: "complaint_filed",
        author: "CFPB Intake Portal",
        content: "FCRA dispute filed through CFPB portal with attached credit report screenshots."
      },
      {
        id: "ev-41",
        timestamp: "2026-08-18T11:30:00Z",
        type: "agent_note",
        author: "Marcus Chen",
        content: "Confirmed system-level error in June Migration Batch #441. 14 other customers affected by same auto-pay drop."
      }
    ],
    recommendedRemediation: {
      action: "Submit Universal Data Form (UDF) / Automated Credit Dispute Verification (ACDV) to Delete Late Mark from all 3 Bureaus Immediately",
      amount: 0.00,
      regulationBasis: "FCRA 15 U.S.C. § 1681s-2 duty to provide accurate information and correct reporting errors within 30 days."
    }
  },
  {
    id: "CMP-2026-8319",
    customerName: "Julian Patel",
    accountNumber: "ACC-774019-55",
    customerTier: "Standard",
    email: "jpatel.dev@gmail.com",
    phone: "+1 (555) 901-7782",
    customerTenure: "1 year",
    customerRiskScore: "Medium (38/100)",
    accountBalance: "$3,150.00",
    title: "ATM Hardware Jam Did Not Dispense Cash But Debited Checking Account",
    product: "Checking & Savings",
    channel: "Mobile App",
    priority: "Medium",
    status: "Resolved",
    disputedAmount: 400.00,
    regulatoryTag: "Regulation E § 1005.11",
    rootCause: "ATM Cash Dispenser Cassette Sensor Fault",
    assignedTo: "Sarah Jenkins",
    createdAt: "2026-08-16T14:10:00Z",
    slaDeadline: "2026-08-19T17:00:00Z",
    sentiment: "Relieved / Satisfied",
    narrative: "Customer attempted to withdraw $400 cash from the Metro Center Branch ATM #04. Machine made grinding noise, displayed 'Technical Out of Service', but the $400 debit appeared on his mobile banking app. Customer requested cash reimbursement.",
    timeline: [
      {
        id: "ev-50",
        timestamp: "2026-08-16T14:10:00Z",
        type: "complaint_filed",
        author: "Julian Patel",
        content: "Mobile dispute logged with ATM identifier #04."
      },
      {
        id: "ev-51",
        timestamp: "2026-08-17T10:00:00Z",
        type: "agent_note",
        author: "Sarah Jenkins",
        content: "ATM Cash Balancing audit confirmed $400 overage in reject cassette #2."
      },
      {
        id: "ev-52",
        timestamp: "2026-08-17T11:15:00Z",
        type: "system_event",
        author: "Core Settlement",
        content: "Permanent credit of $400.00 posted to ACC-774019-55. Case marked Resolved."
      }
    ],
    recommendedRemediation: {
      action: "Permanent Reimbursement of $400.00",
      amount: 400.00,
      regulationBasis: "Regulation E § 1005.11(c) Terminal Error Resolution."
    }
  },
  {
    id: "CMP-2026-8199",
    customerName: "Robert & Cynthia Hayes",
    accountNumber: "ACC-661902-39",
    customerTier: "Preferred",
    email: "robert.hayes@hayeslaw.com",
    phone: "+1 (555) 334-1189",
    customerTenure: "12 years",
    customerRiskScore: "Low (5/100)",
    accountBalance: "$95,000.00",
    title: "Mortgage Escrow Analysis Shortage Spike of $450/month Due to Missed Property Tax Exemption",
    product: "Mortgages & Loans",
    channel: "Phone",
    priority: "Medium",
    status: "Under Investigation",
    disputedAmount: 5400.00,
    regulatoryTag: "RESPA (Real Estate Settlement Procedures Act)",
    rootCause: "Tax Record Indexing Error",
    assignedTo: "Unassigned",
    createdAt: "2026-08-20T10:20:00Z",
    slaDeadline: "2026-08-25T17:00:00Z",
    sentiment: "Concerned / Inquiring",
    narrative: "Annual escrow analysis stated a shortage of $5,400, increasing monthly mortgage payment from $2,800 to $3,250. Customer provided senior property tax exemption certificate which the servicing department failed to index during the county tax assessment pull.",
    timeline: [
      {
        id: "ev-60",
        timestamp: "2026-08-20T10:20:00Z",
        type: "complaint_filed",
        author: "Phone Rep #209",
        content: "Customer called inquiring about 16% mortgage payment jump."
      }
    ],
    recommendedRemediation: {
      action: "Re-run Escrow Analysis with Senior Exemption & Recalculate Monthly Payment",
      amount: 5400.00,
      regulationBasis: "RESPA 12 CFR § 1024.17 escrow account administration guidelines."
    }
  }
];

export const mockAgents = [
  { id: "ag-1", name: "Marcus Chen", role: "Lead Fraud & Regulatory Specialist", activeCases: 3 },
  { id: "ag-2", name: "Sarah Jenkins", role: "Senior Card & Payment Dispute Specialist", activeCases: 2 },
  { id: "ag-3", name: "Elena Rostova", role: "VP Operations & Executive Escalations", activeCases: 1 },
  { id: "ag-4", name: "Devon Miller", role: "Consumer Loan & Escrow Analyst", activeCases: 0 }
];

export const complaintCategories = [
  "All Products",
  "Wire Transfers",
  "Credit Cards",
  "Checking & Savings",
  "Mortgages & Loans",
  "Commercial Banking"
];

export const complaintStatuses = [
  "All Statuses",
  "New",
  "Under Investigation",
  "Pending Customer",
  "Escalated",
  "Resolved"
];

export const complaintPriorities = [
  "All Priorities",
  "Critical",
  "High",
  "Medium",
  "Low"
];
