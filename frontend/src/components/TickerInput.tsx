import React from "react";
import { BaseInput } from "./BaseInput";

interface TickerInputProps {
  ticker: string | undefined;
  onTickerChange: Function;
}

export const TickerInput: React.FC<TickerInputProps> = ({
  ticker,
  onTickerChange,
}) => {
  return (
    <BaseInput
      value={ticker}
      placeholder="AAPL"
      type="text"
      onChange={onTickerChange}
    />
  );
};
