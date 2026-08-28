import React, { useState, useEffect } from 'react';
import { useWorkbench } from '../context/WorkbenchContext';
import { 
  Sparkles, 
  Send, 
  Copy, 
  Check, 
  Scale, 
  ShieldCheck, 
  Bot, 
  Wand2, 
  RefreshCw,
  FileCheck2,
  AlertCircle
} from 'lucide-react';

export const AiResolutionCopilot = ({ complaint }) => {
  const { addTimelineNote, showToast, currentAgent } = useWorkbench();
  const [tone, setTone] = useState('apology'); // 'apology' | 'formal' | 'inforequest'
  const [generatedDraft, setGeneratedDraft] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [copied, setCopied] = useState(false);

  // Generate response letter based on tone and complaint details
  useEffect(() => {
    generateLetter(tone);
  }, [complaint.id, tone]);

  const generateLetter = (selectedTone) => {
    setIsGenerating(true);
    setTimeout(() => {
      let draft = "";
      const customer = complaint.customerName;
      const caseId = complaint.id;
      const amountFormatted = complaint.disputedAmount > 0 
        ? `$${complaint.disputedAmount.toLocaleString(undefined, { minimumFractionDigits: 2 })}` 
        : "";

      if (selectedTone === 'apology') {
        draft = `Dear ${customer},

Thank you for contacting Apex Bank regarding your recent inquiry (Case Reference #${caseId}) concerning the disputed ${complaint.product.toLowerCase()} activity${amountFormatted ? ` of ${amountFormatted}` : ''}.

We understand how frustrating this experience has been, particularly given your valued relationship with Apex Bank. Our fraud and dispute operations team has reviewed the circumstances and verified the transaction discrepancy.

Under our Customer Protection Commitment and applicable regulatory guidelines (${complaint.regulatoryTag || 'Standard Consumer Banking Rules'}), we are pleased to confirm that a full provisional credit${amountFormatted ? ` of ${amountFormatted}` : ''} has been authorized for your account ${complaint.accountNumber}.

We have updated our internal controls to prevent similar occurrences. If you have any further questions, please do not hesitate to reach out directly to our priority resolution desk.

Sincerely,
${currentAgent}
Priority Dispute Resolution Desk
Apex Bank`;
      } else if (selectedTone === 'formal') {
        draft = `OFFICIAL NOTICE OF DISPUTE INVESTIGATION & FINDINGS

Date: ${new Date().toLocaleDateString()}
To: ${customer}
Account: ${complaint.accountNumber}
Dispute Reference ID: ${caseId}

Dear ${customer},

In compliance with federal consumer financial regulations (${complaint.regulatoryTag || '12 CFR § 1005 / § 1026'}), Apex Bank has conducted an investigation regarding your notice of billing error / unauthorized activity.

Investigation Summary:
- Disputed Item: ${complaint.title}
- Disputed Amount: ${amountFormatted || 'N/A'}
- Root Cause Finding: ${complaint.rootCause}

Regulatory Determination:
Pursuant to statutory review requirements, our investigation has concluded. Required adjustments and remediation protocols have been executed in accordance with CFPB regulatory standards.

For complete audit records or to submit supplementary documentation, refer to dispute reference #${caseId}.

Respectfully,
Compliance & Regulatory Operations
Apex Bank`;
      } else {
        draft = `Dear ${customer},

Re: Request for Additional Information - Dispute #${caseId}

We are currently investigating your recent dispute regarding "${complaint.title}". To ensure we resolve your claim promptly and in accordance with regulatory timeframes, we require supplementary documentation.

Please provide the following within 10 business days:
1. Signed dispute affidavit or merchant communication log
2. Itemized receipts or terminal error slip (if applicable)
3. Confirmation of last authorized device access

You may upload these documents directly via the Apex Mobile App under "Dispute Center #${caseId}" or reply securely to this communication.

Thank you for your prompt cooperation.

Sincerely,
${currentAgent}
Dispute Resolution Services
Apex Bank`;
      }

      setGeneratedDraft(draft);
      setIsGenerating(false);
    }, 250);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(generatedDraft);
    setCopied(true);
    showToast('Copied to Clipboard', 'AI response letter copied.', 'info');
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSendToCustomer = () => {
    addTimelineNote(
      complaint.id,
      `AI Response Letter (${tone.toUpperCase()} tone) dispatched to customer (${complaint.email}):\n\n"${generatedDraft.substring(0, 150)}..."`,
      'agent_note'
    );
    showToast('Customer Notified', `Official resolution letter sent to ${complaint.customerName}.`, 'success');
  };

  return (
    <div className="bg-gradient-to-br from-indigo-50/70 via-white to-blue-50/50 dark:from-slate-900 dark:via-slate-900 dark:to-indigo-950/30 rounded-2xl border border-indigo-200/80 dark:border-indigo-900/60 p-5 shadow-sm flex flex-col justify-between">
      
      {/* Copilot Header */}
      <div>
        <div className="flex items-center justify-between pb-3 border-b border-indigo-100 dark:border-indigo-900/60">
          <div className="flex items-center gap-2">
            <div className="p-1.5 bg-indigo-600 text-white rounded-lg shadow-sm shadow-indigo-500/30">
              <Bot className="h-4 w-4" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-bold text-xs text-slate-900 dark:text-white">Gemini Dispute Co-Pilot</span>
                <span className="px-1.5 py-0.2 rounded text-[9px] font-bold bg-indigo-100 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300">
                  AI v3.7
                </span>
              </div>
              <p className="text-[10px] text-slate-500 dark:text-slate-400">Automated policy checks & draft synthesis</p>
            </div>
          </div>

          <button
            onClick={() => generateLetter(tone)}
            title="Re-run AI Analysis"
            className="p-1.5 text-indigo-600 dark:text-indigo-400 hover:bg-indigo-100 dark:hover:bg-indigo-950 rounded-lg transition-colors"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${isGenerating ? 'animate-spin' : ''}`} />
          </button>
        </div>

        {/* AI Insight Pill */}
        <div className="mt-3.5 p-3 rounded-xl bg-white/80 dark:bg-slate-800/80 border border-indigo-100 dark:border-indigo-900/40 text-xs">
          <div className="flex items-center gap-1.5 font-bold text-indigo-900 dark:text-indigo-200 mb-1">
            <Scale className="h-3.5 w-3.5 text-indigo-600 dark:text-indigo-400" />
            <span>Policy Match & Compliance Risk</span>
          </div>
          <p className="text-[11px] text-slate-600 dark:text-slate-300 leading-normal">
            Root cause identified as <strong className="text-slate-800 dark:text-slate-100">{complaint.rootCause}</strong>. 
            Regulatory standard <strong className="text-indigo-600 dark:text-indigo-400">{complaint.regulatoryTag}</strong> applies. 
            Recommended handling time is &lt; 24 business hours.
          </p>
        </div>

        {/* Response Tone Selector */}
        <div className="mt-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-[11px] font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider">
              Draft Customer Communication
            </span>
            <div className="flex items-center gap-1">
              <button
                onClick={() => setTone('apology')}
                className={`px-2 py-1 rounded-lg text-[10px] font-bold transition-all ${
                  tone === 'apology' 
                    ? 'bg-indigo-600 text-white shadow-xs' 
                    : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200'
                }`}
              >
                Expedited Apology
              </button>
              <button
                onClick={() => setTone('formal')}
                className={`px-2 py-1 rounded-lg text-[10px] font-bold transition-all ${
                  tone === 'formal' 
                    ? 'bg-indigo-600 text-white shadow-xs' 
                    : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200'
                }`}
              >
                Formal Notice
              </button>
              <button
                onClick={() => setTone('inforequest')}
                className={`px-2 py-1 rounded-lg text-[10px] font-bold transition-all ${
                  tone === 'inforequest' 
                    ? 'bg-indigo-600 text-white shadow-xs' 
                    : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200'
                }`}
              >
                Info Request
              </button>
            </div>
          </div>

          {/* Letter Draft TextArea */}
          <div className="relative">
            <textarea
              rows={9}
              value={generatedDraft}
              onChange={(e) => setGeneratedDraft(e.target.value)}
              className="w-full p-3 bg-white dark:bg-slate-950/80 border border-slate-200 dark:border-slate-800 rounded-xl text-xs font-mono text-slate-800 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 leading-relaxed resize-none"
            />
          </div>
        </div>
      </div>

      {/* Action Footer */}
      <div className="mt-3 flex items-center justify-between gap-2 pt-2 border-t border-indigo-100 dark:border-indigo-900/60">
        <button
          onClick={handleCopy}
          className="px-3 py-1.5 bg-white dark:bg-slate-800 hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-all"
        >
          {copied ? <Check className="h-3.5 w-3.5 text-emerald-500" /> : <Copy className="h-3.5 w-3.5" />}
          <span>{copied ? 'Copied' : 'Copy Text'}</span>
        </button>

        <button
          onClick={handleSendToCustomer}
          className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-700 active:scale-95 text-white rounded-xl text-xs font-bold flex items-center gap-1.5 shadow-sm shadow-indigo-500/30 transition-all"
        >
          <Send className="h-3.5 w-3.5" />
          <span>Dispatch to Customer</span>
        </button>
      </div>

    </div>
  );
};
