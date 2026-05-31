import {
  FileText, Search, UserCheck, Wrench,
  AlertTriangle, CheckCircle2, Archive, Circle,
} from "lucide-react";

const STEPS = [
  { key: "submitted",    label: "Submitted" },
  { key: "under_review", label: "Under Review" },
  { key: "assigned",     label: "Assigned" },
  { key: "in_progress",  label: "In Progress" },
  { key: "escalated",    label: "Escalated" },
  { key: "resolved",     label: "Resolved" },
  { key: "closed",       label: "Closed" },
];

const STEP_META = {
  submitted:    { Icon: FileText,      desc: "Your complaint has been registered" },
  under_review: { Icon: Search,        desc: "Municipal team is reviewing your complaint" },
  assigned:     { Icon: UserCheck,     desc: "Assigned to a corporator" },
  in_progress:  { Icon: Wrench,        desc: "Work is underway" },
  escalated:    { Icon: AlertTriangle, desc: "Escalated for urgent attention" },
  resolved:     { Icon: CheckCircle2,  desc: "Issue has been resolved" },
  closed:       { Icon: Archive,       desc: "Complaint closed" },
};

const STATUS_ORDER = {
  submitted: 0, under_review: 1, assigned: 2, in_progress: 3,
  escalated: 4, resolved: 5, closed: 6, reopened: 5,
};

function formatDate(d) {
  if (!d) return null;
  return new Date(d).toLocaleString("en-IN", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
}

export default function ComplaintTimeline({ status, statusLog = [], createdAt, slaDeadline }) {
  const currentIndex = STATUS_ORDER[status] ?? 0;
  const isFinished = status === "resolved" || status === "closed";

  const slaDate = slaDeadline ? new Date(slaDeadline) : null;
  const isOverdue = slaDate && slaDate < new Date() && !isFinished;

  const logByStatus = {};
  statusLog.forEach(l => { logByStatus[l.to_status] = l; });

  const filteredSteps = STEPS.filter(s => {
    if (s.key === "escalated") return status === "escalated" || !!logByStatus["escalated"];
    if (s.key === "closed")    return status === "closed"    || !!logByStatus["closed"];
    if (s.key === "assigned")  return !!logByStatus["assigned"];
    return true;
  });

  return (
    <div className="space-y-0">
      {filteredSteps.map((step, idx) => {
        const stepIndex   = STATUS_ORDER[step.key] ?? 0;
        const isDone      = stepIndex < currentIndex;
        const isCurrent   = step.key === status;
        const isPending   = stepIndex > currentIndex && !isCurrent;
        const isLast      = idx === filteredSteps.length - 1;
        const isEscalated = step.key === "escalated";
        const logEntry    = step.key === "submitted" ? { created_at: createdAt } : logByStatus[step.key];
        const { Icon }    = STEP_META[step.key] ?? { Icon: Circle };
        const showSla     = isCurrent && !isFinished && slaDate;

        return (
          <div key={step.key} className="flex gap-3">
            {/* Node + vertical connector */}
            <div className="flex flex-col items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 z-10 transition-all
                ${isDone                           ? "bg-emerald-500"                         : ""}
                ${isCurrent && !isEscalated        ? "bg-primary-500 ring-4 ring-primary-500/20" : ""}
                ${isCurrent &&  isEscalated        ? "bg-red-500 ring-4 ring-red-500/20"      : ""}
                ${isPending                        ? "bg-white border-2 border-gray-200"      : ""}
              `}>
                {isDone    && <Icon className="w-4 h-4 text-white" />}
                {isCurrent && <Icon className="w-4 h-4 text-white animate-pulse" />}
                {isPending && <Circle className="w-3.5 h-3.5 text-gray-300" />}
              </div>
              {!isLast && (
                <div className={`w-0.5 flex-1 my-1 rounded-full ${isDone ? "bg-emerald-200" : "bg-gray-100"}`}
                     style={{ minHeight: 20 }} />
              )}
            </div>

            {/* Content */}
            <div className="pb-5 flex-1 min-w-0 pt-1">
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0 flex-1">
                  <span className={`text-sm font-semibold leading-tight
                    ${isDone                    ? "text-emerald-700"  : ""}
                    ${isCurrent && !isEscalated ? "text-primary-700"  : ""}
                    ${isCurrent &&  isEscalated ? "text-red-700"      : ""}
                    ${isPending                 ? "text-gray-400"     : ""}
                  `}>{step.label}</span>

                  {/* Step description */}
                  {!isPending && (
                    <p className={`text-[11px] mt-0.5 leading-snug
                      ${isDone    ? "text-emerald-500/80" : ""}
                      ${isCurrent ? "text-gray-500"       : ""}
                    `}>{STEP_META[step.key]?.desc}</p>
                  )}

                  {logEntry?.changed_by_name && (
                    <p className="text-xs text-gray-400 mt-0.5">by {logEntry.changed_by_name}</p>
                  )}
                  {logEntry?.remarks && (
                    <p className="text-xs text-gray-500 mt-1.5 bg-gray-50 rounded-lg px-2.5 py-1.5 border border-gray-100 max-w-xs italic">
                      &ldquo;{logEntry.remarks}&rdquo;
                    </p>
                  )}

                  {/* SLA badge on active step */}
                  {showSla && (
                    <div className={`inline-flex items-center gap-1 mt-1.5 text-[10px] font-semibold px-2 py-0.5 rounded-full border
                      ${isOverdue
                        ? "bg-red-50 text-red-600 border-red-200"
                        : "bg-amber-50 text-amber-600 border-amber-200"
                      }`}>
                      {isOverdue ? "⚠ Overdue" : "Due"}: {formatDate(slaDeadline)}
                    </div>
                  )}
                </div>

                {logEntry?.created_at && (
                  <span className="text-[10px] text-gray-400 flex-shrink-0 font-medium whitespace-nowrap">
                    {formatDate(logEntry.created_at)}
                  </span>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
