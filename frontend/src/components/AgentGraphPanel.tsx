import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import type { Message } from "@langchain/langgraph-sdk";
import type { ProcessedEvent } from "./ActivityTimeline";
import { cn } from "../lib/utils";

type StepKey =
  | "orchestrator"
  | "generate"
  | "research"
  | "reflection"
  | "finalize";

function stepFromEvents(events: ProcessedEvent[] | undefined): StepKey {
  const lastTitle = events?.[events.length - 1]?.title?.toLowerCase() ?? "";
  if (lastTitle.includes("generating")) return "generate";
  if (lastTitle.includes("research")) return "research";
  if (lastTitle.includes("reflection")) return "reflection";
  if (lastTitle.includes("finalizing")) return "finalize";
  return "orchestrator";
}

function statusFromStep(step: StepKey, isLoading: boolean): string {
  if (!isLoading) return "Idle";
  switch (step) {
    case "generate":
      return "Generating queries";
    case "research":
      return "Searching sources";
    case "reflection":
      return "Reflecting";
    case "finalize":
      return "Finalizing";
    default:
      return "Routing";
  }
}

function Node({
  label,
  active,
  x,
  y,
}: {
  label: string;
  active: boolean;
  x: number;
  y: number;
}) {
  return (
    <g>
      <circle
        cx={x}
        cy={y}
        r={10}
        className={cn(
          "fill-neutral-600",
          active && "fill-neutral-300"
        )}
      />
      <text
        x={x + 18}
        y={y + 4}
        className={cn(
          "fill-neutral-200 text-[12px]",
          active && "fill-neutral-100"
        )}
      >
        {label}
      </text>
    </g>
  );
}

export function AgentGraphPanel({
  isLoading,
  messages,
  liveActivityEvents,
  historicalActivities,
  onSubmit,
}: {
  isLoading: boolean;
  messages: Message[];
  liveActivityEvents: ProcessedEvent[];
  historicalActivities: Record<string, ProcessedEvent[]>;
  onSubmit: (inputValue: string, effort: string, model: string) => void;
}) {
  const lastMessage = messages[messages.length - 1];
  const historicalForLastAi =
    lastMessage?.type === "ai" && lastMessage.id
      ? historicalActivities[lastMessage.id]
      : undefined;

  const activeEvents = isLoading ? liveActivityEvents : historicalForLastAi;
  const activeStep = stepFromEvents(activeEvents);
  const status = statusFromStep(activeStep, isLoading);

  const demoModel = "gemini-2.5-flash-preview-04-17";

  return (
    <Card className="h-full border-neutral-700 bg-neutral-800">
      <CardHeader className="pb-3">
        <CardTitle className="text-sm text-neutral-100">Agent Graph</CardTitle>
        <div className="text-xs text-neutral-400">Status: {status}</div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="rounded-lg border border-neutral-700 bg-neutral-900/30 p-3">
          <svg viewBox="0 0 280 160" className="w-full h-[160px]">
            <line
              x1={20}
              y1={30}
              x2={20}
              y2={130}
              className="stroke-neutral-700"
              strokeWidth={2}
            />
            <line
              x1={20}
              y1={30}
              x2={120}
              y2={30}
              className="stroke-neutral-700"
              strokeWidth={2}
            />
            <line
              x1={20}
              y1={60}
              x2={120}
              y2={60}
              className="stroke-neutral-700"
              strokeWidth={2}
            />
            <line
              x1={20}
              y1={90}
              x2={120}
              y2={90}
              className="stroke-neutral-700"
              strokeWidth={2}
            />
            <line
              x1={20}
              y1={120}
              x2={120}
              y2={120}
              className="stroke-neutral-700"
              strokeWidth={2}
            />

            <Node
              label="Orchestrator"
              active={activeStep === "orchestrator"}
              x={20}
              y={30}
            />
            <Node
              label="Generate queries"
              active={activeStep === "generate"}
              x={120}
              y={30}
            />
            <Node
              label="Web research"
              active={activeStep === "research"}
              x={120}
              y={60}
            />
            <Node
              label="Reflection"
              active={activeStep === "reflection"}
              x={120}
              y={90}
            />
            <Node
              label="Finalize answer"
              active={activeStep === "finalize"}
              x={120}
              y={120}
            />
          </svg>
        </div>

        <div className="space-y-2">
          <div className="text-xs text-neutral-400">Quick demo actions</div>
          <div className="flex flex-col gap-2">
            <Button
              variant="default"
              className="bg-neutral-700 border-neutral-600 text-neutral-200 justify-start"
              disabled={isLoading}
              onClick={() =>
                onSubmit(
                  "Készíts egy rövid kutatási összefoglalót: mik a 2025-ös trendek a multi-agent rendszerekben? Adj forrásokat.",
                  "medium",
                  demoModel
                )
              }
            >
              Run research demo
            </Button>
            <Button
              variant="default"
              className="bg-neutral-700 border-neutral-600 text-neutral-200 justify-start"
              disabled={isLoading}
              onClick={() =>
                onSubmit(
                  "Írj Python kódot: egy FastAPI endpoint, ami API kulcsot ellenőriz X-API-Key headerből. Csak kódot adj vissza.",
                  "medium",
                  demoModel
                )
              }
            >
              Run coding demo
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
