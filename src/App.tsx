import "./index.css";
import { Portfolio } from "./components";

export default function App() {
  return (
    <div className="h-screen flex items-center flex-col w-1/2 m-auto">
      <div className="pt-8 flex flex-col justify-center items-center">
        <span className="font-semibold text-2xl">
          Portfolio Variance Calculator
        </span>
        <span className="text-sm italic text-center w-2/3 mt-2">
          Enter the ticker for each asset along with the corresponding number of
          shares. Calculations leverage one year daily returns.
        </span>
      </div>
      <Portfolio />
    </div>
  );
}
