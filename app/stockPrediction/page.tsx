"use client";

import Link from "next/link";
import { useState } from "react";
import { Line } from "react-chartjs-2";
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
} from "chart.js";

// Register required components
ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
);

export default function Predictions() {
    const [symbol, setSymbol] = useState("");
    const [days, setDays] = useState(7);
    const [data, setData] = useState<Record<string, number> | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const fetchPredictions = async () => {
        setError(null);
        setData(null);

        if (!symbol.trim()) {
            setError("Please enter a valid stock ticker.");
            return;
        }
        if (days <= 0) {
            setError("Number of days must be greater than 0.");
            return;
        }

        setLoading(true);
        try {
            const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
            const res = await fetch(`${baseUrl}/api/py/stock/predict/${symbol}?days=${days}`);

            if (!res.ok) {
                const errorText = await res.text();
                throw new Error(errorText || "Failed to fetch predictions.");
            }

            const result = await res.json();

            if (!result || typeof result !== "object") {
                throw new Error("Invalid response from the server.");
            }

            setData(result);
        } catch (err) {
            setError((err as Error).message || "Unknown error occurred.");
        } finally {
            setLoading(false);
        }
    };

    const chartData = data
        ? {
              labels: Object.keys(data.predictions),
              datasets: [
                  {
                      label: `Predicted Prices for ${data.symbol}`,
                      data: Object.values(data.predictions),
                      borderColor: "rgba(75, 192, 192, 1)",
                      backgroundColor: "rgba(75, 192, 192, 0.2)",
                      tension: 0.3,
                  },
              ],
          }
        : null;

    return (
        <main className="flex min-h-screen flex-col items-center justify-center p-10 space-y-10">
            <h1 className="text-3xl font-bold">Stock Predictions</h1>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl w-full">
                {/* Input Section */}
                <div className="p-6 bg-gray-100 dark:bg-neutral-800 rounded-lg shadow-md space-y-4">
                    <input
                        className="rounded-lg border border-transparent p-2 w-full text-black"
                        type="text"
                        placeholder="Enter Stock Symbol (e.g., SPY)"
                        value={symbol}
                        onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                    />
                    <input
                        className="rounded-lg border border-transparent p-2 w-full text-black"
                        type="number"
                        placeholder="Number of Days"
                        value={days}
                        onChange={(e) => setDays(Number(e.target.value))}
                        min={1}
                    />
                    <button
                        className="rounded-lg border border-transparent w-full px-10 py-4 transition-colors hover:border-gray-300 hover:bg-gray-100 hover:dark:border-neutral-700 hover:dark:bg-neutral-800/30"
                        onClick={fetchPredictions}
                    >
                        Get Predictions
                    </button>
                </div>

                {/* Results Section */}
                <div className="p-6 bg-gray-100 dark:bg-neutral-800 rounded-lg shadow-md">
                    {loading && <p className="text-center text-gray-500">Loading...</p>}
                    {error && <p className="text-red-500 text-center">{error}</p>}
                    {chartData && (
                        <div className="mt-4">
                            <Line data={chartData} />
                        </div>
                    )}
                    {!loading && !data && !error && (
                        <p className="text-center text-gray-500">
                            Enter a stock ticker and the number of days to see predictions.
                        </p>
                    )}
                </div>
            </div>

            {/* Navigation Section */}
            <div>
              <Link
                href="/"
                className="group rounded-lg border border-transparent px-10 py-4 flex items-center transition-colors hover:border-gray-300 hover:bg-gray-100 hover:dark:border-neutral-700 hover:dark:bg-neutral-800/30"
              >
                <span className="inline-block transition-transform group-hover:-translate-x-1 motion-reduce:transform-none">
                  &lt;-
                </span>
                <h2 className={`ml-2 mb-0 text-xl font-semibold`}>
                {" "}Back to Homepage
                </h2>
              </Link>
            </div>
        </main>
    );
}




