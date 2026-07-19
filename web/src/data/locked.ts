import locked from "../../public/locked_evaluation.json";

export type DecisionKey = "keep" | "reshape" | "deemphasize";

export const lockedReport = locked;

export const lockedCase = locked.case;
export const lockedEffect = locked.effect;
export const lockedOptions = locked.options;

export function formatSigned(value: number, digits = 2): string {
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(digits)}`;
}
