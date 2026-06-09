import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { CheckCircle2, AlertTriangle, MessageSquare, FileText, ClipboardCheck } from "lucide-react";

function ScoreBadge({ pass, score }) {
  const label = `${score?.toFixed ? score.toFixed(1) : score} / 5`;
  return (
    <Badge className={pass ? "bg-green-600 text-white" : "bg-red-600 text-white"}>
      {pass ? "PASS" : "FAIL"} · {label}
    </Badge>
  );
}

export default function InclusionResult() {
  const reviewers = props.reviewers || [];
  const evalResult = props.evalResult || { overall_score: 0, overall_pass: false, evals: [] };
  const jobPosting = props.jobPosting || "";

  return (
    <div className="w-full grid grid-cols-12 gap-4 mt-2">
      {/* LEFT: agent reasoning */}
      <div className="col-span-12 md:col-span-3 flex flex-col gap-2">
        <div className="flex items-center gap-2 text-sm font-semibold text-muted-foreground">
          <MessageSquare className="h-4 w-4" /> Agent reasoning
        </div>
        {reviewers.length === 0 && (
          <Card className="p-3 text-sm text-muted-foreground">No reviewers ran.</Card>
        )}
        {reviewers.map((r, i) => {
          const hasSuggestions = (r.suggestions || []).length > 0;
          return (
            <Card key={i} className="p-3 flex flex-col gap-2">
              <div className="flex items-center gap-2">
                {hasSuggestions ? (
                  <AlertTriangle className="h-4 w-4 text-amber-500" />
                ) : (
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                )}
                <span className="text-xs font-mono">{r.reviewer}</span>
              </div>
              <div className="text-sm">{r.summary}</div>
              {hasSuggestions && (
                <ul className="text-xs text-muted-foreground list-disc pl-4 space-y-1">
                  {r.suggestions.map((s, j) => (
                    <li key={j}>{s}</li>
                  ))}
                </ul>
              )}
              {(r.evidence_spans || []).length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {r.evidence_spans.map((e, j) => (
                    <Badge key={j} variant="outline" className="text-[10px]">
                      {e}
                    </Badge>
                  ))}
                </div>
              )}
            </Card>
          );
        })}
      </div>

      {/* CENTER: the job posting outcome */}
      <div className="col-span-12 md:col-span-6 flex flex-col gap-2">
        <div className="flex items-center gap-2 text-sm font-semibold text-muted-foreground">
          <FileText className="h-4 w-4" /> Job posting
        </div>
        <Card className="p-4 whitespace-pre-wrap text-sm leading-relaxed">
          {jobPosting}
        </Card>
      </div>

      {/* RIGHT: evaluation outcome */}
      <div className="col-span-12 md:col-span-3 flex flex-col gap-2">
        <div className="flex items-center gap-2 text-sm font-semibold text-muted-foreground">
          <ClipboardCheck className="h-4 w-4" /> Inclusion evals
        </div>
        <Card className="p-3 flex items-center justify-between">
          <span className="text-sm font-medium">Overall</span>
          <ScoreBadge pass={evalResult.overall_pass} score={evalResult.overall_score} />
        </Card>
        {(evalResult.evals || []).map((e, i) => (
          <Card key={i} className="p-3 flex flex-col gap-1">
            <div className="flex items-center justify-between gap-2">
              <span className="text-xs font-medium">{e.eval_name}</span>
              <ScoreBadge pass={e.pass} score={e.score} />
            </div>
            <Separator />
            <div className="text-xs text-muted-foreground">{e.rationale}</div>
          </Card>
        ))}
      </div>
    </div>
  );
}
