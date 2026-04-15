"use client";

import { TooltipProvider } from "@/components/ui/tooltip";
import AssistantHome from "@/screens/AssistantHome";

export default function HomePage() {
  return (
    <TooltipProvider>
      <AssistantHome />
    </TooltipProvider>
  );
}
