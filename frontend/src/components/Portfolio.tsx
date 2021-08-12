import React, { useState } from "react";
import { SharesInput } from "./SharesInput";
import { TickerInput } from "./TickerInput";
import update from "immutability-helper";
import axios from "axios";
import { XClose } from "./XClose";

interface PortfolioProps {}

interface PortfolioStats {
  variance?: number;
  sd?: number;
}

export const Portfolio: React.FC<PortfolioProps> = () => {
  const [tickers, setTickers] = useState<(string | undefined)[]>([
    "AAPL",
    "MSFT",
  ]);
  const [shares, setShares] = useState<number[]>([20, 10]);
  const [stats, setStats] = useState<PortfolioStats>({});
  const [calculating, setCalculating] = useState<boolean>(false);

  function onTickerChange(index: number, newTicker: string) {
    setTickers((tickers) =>
      update(tickers, {
        [index]: {
          $set: newTicker,
        },
      })
    );
  }

  function onSharesChange(index: number, newShares: number) {
    setShares((shares) =>
      update(shares, {
        [index]: {
          $set: newShares,
        },
      })
    );
  }

  function onPairRemoved(index: number) {
    setTickers((tickers) =>
      update(tickers, {
        $splice: [[index, 1]],
      })
    );

    setShares((shares) =>
      update(shares, {
        $splice: [[index, 1]],
      })
    );
  }

  function onAssetAdded() {
    setTickers((tickers) =>
      update(tickers, {
        $push: [""],
      })
    );

    setShares((shares) =>
      update(shares, {
        $push: [0],
      })
    );
  }

  function onClearAll() {
    setTickers([]);
    setShares([]);
  }

  async function fetchStats() {
    setStats({});
    setCalculating(true);

    const { data } = await axios.post(
      "https://portfolio-variance-calculator.herokuapp.com/variance",
      {
        portfolio: tickers.reduce((acc, ticker, index) => {
          if (ticker && shares[index] !== 0) {
            acc[ticker] = shares[index];
          }
          return acc;
        }, {} as Record<string, number>),
      }
    );

    const { variance, sd } = data;

    setStats({
      variance,
      sd,
    });
    setCalculating(false);
  }

  return (
    <div className="w-full">
      {tickers.map((ticker, index) => {
        return (
          <div className="my-8 flex space-x-4 items-center" key={ticker}>
            <TickerInput
              ticker={ticker}
              onTickerChange={(e: any) => onTickerChange(index, e.target.value)}
            />
            <SharesInput
              quantity={shares[index]}
              onSharesChange={(e: any) =>
                onSharesChange(index, e.target.valueAsNumber)
              }
            />
            <button
              onClick={() => onPairRemoved(index)}
              className="rounded-full flex-none flex items-center justify-center font-bold text-xs"
            >
              <XClose size={24} />
            </button>
          </div>
        );
      })}
      <div className={`flex space-x-4 ${tickers.length === 0 ? "mt-8" : ""}`}>
        <button
          className="rounded text-white bg-green-500 hover:bg-green-700 w-full py-2 uppercase tracking-widest font-semibold"
          onClick={onAssetAdded}
        >
          Add Asset
        </button>
        <button
          className="rounded text-white bg-red-500 hover:bg-red-700 w-full py-2 uppercase tracking-widest font-semibold"
          onClick={onClearAll}
        >
          Clear All
        </button>
      </div>
      <div className="flex justify-center my-8">
        {tickers.length >= 1 ? (
          <button
            className="rounded text-white bg-purple-500 hover:bg-purple-700 py-2 w-full uppercase font-semibold tracking-widest"
            onClick={() => fetchStats()}
          >
            Calculate
          </button>
        ) : (
          <span className="text-red-500 font-semibold text-lg">
            {" "}
            Need at least 1 asset to perform calculation!
          </span>
        )}
      </div>
      {calculating ? (
        <div className="leading-tight font-light flex justify-center text-lg items-center">
          {" "}
          Calculating...{" "}
        </div>
      ) : (
        <div className="flex space-x-12 justify-center text-lg">
          <div className="flex flex-col">
            <span className="leading-tight font-light">Variance </span>
            <span className="font-semibold text-center">
              {stats.variance ? `${(stats.variance * 100).toFixed(2)}%` : "--"}
            </span>
          </div>
          <div className="flex flex-col">
            <span className="leading-tight font-light">
              Standard Deviation{" "}
            </span>
            <span className="font-semibold text-center">
              {stats.sd ? `${(stats.sd * 100).toFixed(2)}%` : "--"}
            </span>
          </div>
        </div>
      )}
    </div>
  );
};
