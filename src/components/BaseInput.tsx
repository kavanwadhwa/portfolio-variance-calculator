import React from "react";

interface BaseInputProps {
  [key: string]: any;
  onChange: any;
}

export const BaseInput: React.FC<BaseInputProps> = (props) => {
  return (
    <input
      className="appearance-none block w-full bg-gray-200 text-gray-700 border border-gray-200 rounded py-3 px-4 leading-tight focus:outline-none focus:border-gray-500"
      {...props}
    />
  );
};
