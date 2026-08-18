import { useState } from "react"

export function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col items-center justify-center gap-6">

      <h1 className="text-5xl font-bold text-blue-500">
        YouTube RAG Chatbot
      </h1>

      <div className="text-3xl font-semibold">
        Count: {count}
      </div>

      <div className="flex gap-4">

        <button
          onClick={() => setCount(count == 9 ? 0 : count + 1)}
          className="px-6 py-3 rounded-lg bg-green-600 hover:bg-green-700 font-semibold transition cursor-pointer"
        >
          Increment
        </button>

        <button
          onClick={() => setCount(count == 0 ? 0 : count - 1)}
          className="px-6 py-3 rounded-lg bg-red-600 hover:bg-red-700 font-semibold transition cursor-pointer"
        >
          Decrement
        </button>

      </div>

    </div>
  )
}