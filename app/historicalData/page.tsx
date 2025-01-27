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

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
);

export default function HistoricalData() {
    const [symbol, setSymbol] = useState("");
    const [data, setData] = useState<any>(null);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const fetchHistoricalData = async () => {
        setError(null);
        setData(null);

        if (!symbol.trim()) {
            setError("Please enter a valid stock ticker.");
            return;
        }

        setLoading(true);
        try {
            const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
            const res = await fetch(`${baseUrl}/api/py/stock/${symbol}`);
            if (!res.ok) {
                throw new Error("Failed to fetch historical data. Please check the stock ticker.");
            }

            const result = await res.json();
            setData(result);
        } catch (err) {
            setError((err as Error).message);
        } finally {
            setLoading(false);
        }
    };

    const getChartData = (key: string) => {
        if (!data) return null;
    
        // Ensure data[key] is being accessed correctly
        const labels = Object.keys(data).map((date) =>
            new Date(date).toLocaleDateString("en-US", {
                year: "2-digit",
                month: "2-digit",
                day: "2-digit",
            })
        );
    
        const datasetValues = Object.keys(data).map((date) => {
            const value = data[date][key];
            return value !== undefined ? value : null; // Ensure valid data
        });
    
        return {
            labels,
            datasets: [
                {
                    label: `${key} Prices`,
                    data: datasetValues,
                    borderColor: "rgba(75, 192, 192, 1)",
                    backgroundColor: "rgba(75, 192, 192, 0.2)",
                    tension: 0.3,
                },
            ],
        };
    };

    const renderChart = (key: string, title: string) => {
        const chartData = getChartData(key);

        if (!chartData) {
            return <p className="text-center text-gray-500">No data available for {title}.</p>;
        }

        return (
            <div className="p-6 bg-gray-100 dark:bg-neutral-800 rounded-lg shadow-md">
                <h2 className="text-xl font-bold text-center mb-4">{title}</h2>
                <Line data={chartData} />
            </div>
        );
    };

    return (
        <main className="flex min-h-screen flex-col items-center justify-center p-10 space-y-10">
            <h1 className="text-3xl font-bold">Historical Stock Data</h1>

            {/* Input Section */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-6xl w-full">
                <div className="p-6 bg-gray-100 dark:bg-neutral-800 rounded-lg shadow-md space-y-4">
                    <input
                        className="rounded-lg border border-transparent p-2 w-full text-black"
                        type="text"
                        placeholder="Enter Stock Symbol (e.g., AAPL)"
                        value={symbol}
                        onChange={(e) => setSymbol(e.target.value)}
                    />
                    <button
                        className="rounded-lg border border-transparent w-full px-10 py-4 transition-colors hover:border-gray-300 hover:bg-gray-100 hover:dark:border-neutral-700 hover:dark:bg-neutral-800/30"
                        onClick={fetchHistoricalData}
                    >
                        Get Data
                    </button>
                </div>

                {/* Navigation Section */}
                <div>
                    <Link
                        href="/"
                        className="group rounded-lg border border-transparent px-6 py-4 flex justify-center items-center transition-colors hover:border-gray-300 hover:bg-gray-100 hover:dark:border-neutral-700 hover:dark:bg-neutral-800/30"
                    >
                        <span className="inline-block transition-transform group-hover:-translate-x-1 motion-reduce:transform-none">
                            &lt;-
                        </span>
                        <h2 className={`ml-2 mb-0 text-xl font-semibold text-center`}>
                            {" "}Back to Homepage
                        </h2>
                    </Link>
                </div>
            </div>

            {/* Loading and Error States */}
            {loading && <p className="text-center text-gray-500">Loading...</p>}
            {error && <p className="text-center text-red-500">{error}</p>}

            {/* Render Charts */}
            {data && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-6xl w-full">
                    {renderChart("Open", "Open Prices")}
                    {renderChart("Close", "Close Prices")}
                    {renderChart("High", "High Prices")}
                    {renderChart("Low", "Low Prices")}
                </div>
            )}

            {/* Render Table */}
            {data && (
                <div className="bg-transparent rounded-lg shadow-md w-full">
                    <h2 className="text-xl font-bold text-center mb-4">Detailed Data</h2>
                    <table className="w-full border-collapse border border-gray-300 rounded-lg">
                        <thead className="sticky top-0 bg-gray-100 dark:bg-neutral-800">
                            <tr>
                                <th className="border px-4 py-2 text-center">Date</th>
                                <th className="border px-4 py-2 text-center">Open</th>
                                <th className="border px-4 py-2 text-center">High</th>
                                <th className="border px-4 py-2 text-center">Low</th>
                                <th className="border px-4 py-2 text-center">Close</th>
                                <th className="border px-4 py-2 text-center">Volume</th>
                            </tr>
                        </thead>
                        <tbody>
                            {Object.keys(data).map((date) => (
                                <tr key={date}>
                                    <td className="border px-4 py-2">
                                        {new Date(date).toLocaleDateString("en-US", {
                                            year: "2-digit",
                                            month: "2-digit",
                                            day: "2-digit",
                                        })}
                                    </td>
                                    <td className="border px-4 py-2">{data[date]["Open"].toFixed(2)}</td>
                                    <td className="border px-4 py-2">{data[date]["High"].toFixed(2)}</td>
                                    <td className="border px-4 py-2">{data[date]["Low"].toFixed(2)}</td>
                                    <td className="border px-4 py-2">{data[date]["Close"].toFixed(2)}</td>
                                    <td className="border px-4 py-2">{data[date]["Volume"]}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </main>
    );
}



