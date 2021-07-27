import React from "react";
import { BaseInput } from "./BaseInput";

interface SharesInputProps {
  quantity: number;
  onSharesChange: Function;
}

export const SharesInput: React.FC<SharesInputProps> = ({
  quantity,
  onSharesChange,
}) => {
  return (
    <BaseInput
      value={quantity}
      placeholder="1"
      type="number"
      min={1}
      onChange={onSharesChange}
    />
  );
};
