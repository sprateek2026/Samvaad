import { CheckCircle2, Circle, Clock } from "lucide-react";

const STEPS = [
  { key: "submitted",    label: "Submitted" },
  { key: "under_review", label: "Under Review" },
  { key: "assigned",     label: "Assigned" },
  { key: "in_progress",  label: "In Progress" },
  { key: "escalated",    label: "Escalated" },
  { key: "resolved",     label: "Resolved" },
  { key: "closed",       label: "Closed" },
];

const STATUS_ORDER = {
  submitted: 0, under_review: 1, assigned: 2, in_progress: 3,
  escalated: 4, resolved: 5, closed: 6, reopened: 5,
};

function formatDate(d) {
  if (!d) return null;
  return new Date(d).toLocaleString("en-IN", { day: "numeric", month: "short", hour: "2-digit", minute: "2-digit" });
}

export default function ComplaintTimeline({ status, statusLog = [], createdAt }) {
  const currentIndex = STATUS_ORDER[status] ?? 0;

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
        const stepIndex  = STATUS_ORDER[step.key] ?? 0;
        const isDone     = stepIndex < currentIndex;
        const isCurrent  = step.key === status;
        const isPending  = stepIndex > currentIndex && !isCurrent;
        const isLast     = idx === filteredSteps.length - 1;
        const isEscalated = step.key === "escalated";
        const logEntry   = step.key === "submitted" ? { created_at: createdAt } : logByStatus[step.key];

        return (
          <div key={step.key} className="flex gap-3">
            {/* Node + vertical connector */}
            <div className="flex flex-col items-center">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 z-10 transition-all
                ${isDone     ? "bg-emerald-500"                             : ""}
                ${isCurrent && !isEscalated ? "bg-primary-500 ring-4 ring-primary-500/20" : ""}
                ${isCurrent &&  isEscalated ? "bg-red-500 ring-4 ring-red-500/20"         : ""}
                ${isPending  ? "bg-white border-2 border-gray-200"          : ""}
              `}>
                {isDone    && <CheckCircle2 className="w-4 h-4 text-white" />}
                {isCurrent && <Clock className={`w-4 h-4 text-white ${isCurrent ? "animate-pulse" : ""}`} />}
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
                <div>
                  <span className={`text-sm font-semibold leading-tight
                    ${isDone     ? "text-emerald-700"  : ""}
                    ${isCurrent && !isEscalated ? "text-primary-700"  : ""}
                    ${isCurrent &&  isEscalated ? "text-red-700"      : ""}
                    ${isPending  ? "text-gray-400"     : ""}
                  `}>{step.label}</span>
                  {logEntry?.changed_by_name && (
                    <p className="text-xs text-gray-400 mt-0.5">by {logEntry.changed_by_name}</p>
                  )}
                  {logEntry?.remarks && (
                    <p className="text-xs text-gray-500 mt-1.5 bg-gray-50 rounded-lg px-2.5 py-1.5 border border-gray-100 max-w-xs italic">
                      "{logEntry.remarks}"
                    </p>
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
