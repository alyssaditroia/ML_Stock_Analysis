"use client";

import Link from "next/link";
import { useState, useEffect } from "react";
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

// Register required Chart.js components
ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
);

export default function Dashboard() {
    const [metrics, setMetrics] = useState<any[] | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const fetchMetrics = async () => {
            setError(null);
            setLoading(true);

            try {
                const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
                const res = await fetch(`${baseUrl}/api/py/model/metrics`);
                if (!res.ok) {
                    throw new Error("Failed to fetch metrics.");
                }
                const result = await res.json();
                setMetrics(result);
            } catch (err) {
                setError((err as Error).message || "Unknown error occurred.");
            } finally {
                setLoading(false);
            }
        };

        fetchMetrics();
    }, []);

    const getChartData = (metricKey: string) => {
        if (!metrics || metrics.length === 0) return null;

        return {
            labels: metrics.map((entry: any) => entry.period), // Example: ['1mo', '3mo', '6mo']
            datasets: [
                {
                    label: metricKey,
                    data: metrics.map((entry: any) => entry[metricKey] || 0), // Use 0 for missing data
                    borderColor: "rgba(75, 192, 192, 1)",
                    backgroundColor: "rgba(75, 192, 192, 0.2)",
                    tension: 0.3,
                },
            ],
        };
    };

    const renderChart = (metricKey: string, title: string) => {
        const chartData = getChartData(metricKey);

        if (!chartData) {
            return <p className="text-center text-gray-500">No data available for {title}.</p>;
        }

        return <Line data={chartData} />;
    };

    return (
        <main className="flex min-h-screen flex-col items-center justify-center p-10 space-y-10">
            <h1 className="text-3xl font-bold">Model Evaluation Dashboard</h1>

            {loading && <p className="text-center text-gray-500">Loading...</p>}
            {error && <p className="text-red-500 text-center">{error}</p>}

            {!loading && metrics && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-6xl w-full">
                    {/* RMSE Chart */}
                    <div className="p-6 bg-gray-100 dark:bg-neutral-800 rounded-lg shadow-md">
                        <h2 className="text-xl font-bold text-center mb-4">Root Mean Squared Error (RMSE)</h2>
                        {renderChart("rmse", "RMSE")}
                    </div>

                    {/* MAE Chart */}
                    <div className="p-6 bg-gray-100 dark:bg-neutral-800 rounded-lg shadow-md">
                        <h2 className="text-xl font-bold text-center mb-4">Mean Absolute Error (MAE)</h2>
                        {renderChart("mae", "MAE")}
                    </div>

                    {/* MSE Chart */}
                    <div className="p-6 bg-gray-100 dark:bg-neutral-800 rounded-lg shadow-md">
                        <h2 className="text-xl font-bold text-center mb-4">Mean Squared Error (MSE)</h2>
                        {renderChart("mse", "MSE")}
                    </div>

                    {/* Accuracy Chart */}
                    <div className="p-6 bg-gray-100 dark:bg-neutral-800 rounded-lg shadow-md">
                        <h2 className="text-xl font-bold text-center mb-4">Model Accuracy</h2>
                        {renderChart("accuracy", "Accuracy")}
                    </div>
                </div>
            )}

            {/* Navigation Section */}
            <div>
                <Link
                    href="/"
                    className="group rounded-lg border border-transparent px-10 py-4 flex items-center transition-colors hover:border-gray-300 hover:bg-gray-100 hover:dark:border-neutral-700 hover:dark:bg-neutral-800/30"
                >
                    <span className="inline-block transition-transform group-hover:-translate-x-1 motion-reduce:transform-none">
                        &lt;-
                    </span>
                    <h2 className="ml-2 mb-0 text-xl font-semibold">
                        Back to Homepage
                    </h2>
                </Link>
            </div>
        </main>
    );
}



