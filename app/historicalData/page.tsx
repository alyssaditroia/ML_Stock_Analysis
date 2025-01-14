"use client";

import Link from "next/link";
import { useState } from "react";

export default function History() {
  const [ticker, setTicker] = useState(""); // State to store user input
  interface StockData {
    Open: { [key: string]: number };
    High: { [key: string]: number };
    Low: { [key: string]: number };
    Close: { [key: string]: number };
    Volume: { [key: string]: number };
  }

  const [data, setData] = useState<StockData | null>(null); // State to store fetched data
  const [error, setError] = useState<string | null>(""); // State to store error messages
  const [loading, setLoading] = useState(false); // State to show loading indicator

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault(); // Prevent page reload
    setError(null); // Clear previous errors
    setData(null); // Clear previous data
    if (ticker.trim() === "") {
      setError("Please enter a valid stock ticker.");
      return;
    }

    setLoading(true); // Show loading indicator
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/py/stock/${ticker}`);
      if (!response.ok) {
        throw new Error("Failed to fetch stock data. Please check the ticker symbol.");
      }
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false); // Hide loading indicator
    }
  };

  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <h1 className="text-3xl font-bold">Stock History</h1>
      <p className="mt-4">Welcome to the Stock History page!</p>

      <form onSubmit={handleSearch} className="mt-8">
        <input
          type="text"
          placeholder="Enter stock ticker (e.g., AAPL)"
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
          className="border p-2 rounded mr-2"
        />
        <button
          type="submit"
          className="bg-blue-500 text-white px-4 py-2 rounded"
        >
          Search
        </button>
      </form>

      {loading && <p className="mt-4">Loading...</p>}

      {error && <p className="mt-4 text-red-500">{error}</p>}

      {data && (
        <div className="mt-8 w-full max-w-3xl">
          <h2 className="text-2xl font-semibold mb-4">Stock Data for {ticker}</h2>
          <table className="w-full border-collapse border border-gray-300">
            <thead>
              <tr>
                <th className="border border-gray-300 px-4 py-2">Date</th>
                <th className="border border-gray-300 px-4 py-2">Open</th>
                <th className="border border-gray-300 px-4 py-2">High</th>
                <th className="border border-gray-300 px-4 py-2">Low</th>
                <th className="border border-gray-300 px-4 py-2">Close</th>
                <th className="border border-gray-300 px-4 py-2">Volume</th>
              </tr>
            </thead>
            <tbody>
              {Object.keys(data.Open).map((dateTime) => {
                const date = dateTime.split("T")[0]; // Format date
                return (
                  <tr key={date}>
                    <td className="border border-gray-300 px-4 py-2">{date}</td>
                    <td className="border border-gray-300 px-4 py-2">{data.Open[dateTime].toFixed(2)}</td>
                    <td className="border border-gray-300 px-4 py-2">{data.High[dateTime].toFixed(2)}</td>
                    <td className="border border-gray-300 px-4 py-2">{data.Low[dateTime].toFixed(2)}</td>
                    <td className="border border-gray-300 px-4 py-2">{data.Close[dateTime].toFixed(2)}</td>
                    <td className="border border-gray-300 px-4 py-2">{data.Volume[dateTime]}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </main>
  );
}
