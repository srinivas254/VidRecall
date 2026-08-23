import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { VidRecallLogo } from "./logo.jsx";

export function ChatSession() {
  const navigate = useNavigate();
  const location = useLocation();

  const { source, videoId } = location.state || {};

  const [message, setMessage] = useState("");

  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Your video is ready. Ask me anything about its content.",
    },
  ]);

  const handleSend = async () => {
    if (!message.trim()) return;

    const userQuestion = message.trim();

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: userQuestion,
      },
    ]);

    setMessage("");

    try {
      const response = await fetch(
        `http://localhost:8000/chat/${videoId}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            source: source,
            question: userQuestion,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail);
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer,
        },
      ]);
    } catch (error) {
      console.error("Chat error:", error);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Sorry, something went wrong. Please try again.",
        },
      ]);
    }
  };

  return (
    <div className="h-screen bg-gray-950 text-white flex flex-col">

      <header
        className="
          shrink-0
          border-b
          border-gray-800
          px-4
          py-4
          sm:px-6
          sm:py-5
          lg:px-8
        "
      >
        <div className="flex items-center justify-between">
          <div
            onClick={() => navigate("/")}
            className="cursor-pointer"
          >
            <VidRecallLogo />
          </div>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto">

        <div
          className="
            mx-auto
            w-full
            max-w-4xl
            px-4
            py-6
            sm:px-6
            sm:py-8
          "
        >
          <div className="flex flex-col gap-4 sm:gap-6">

            {messages.map((msg, index) => (
              <div
                key={index}
                className={`
                  flex
                  ${
                    msg.role === "user"
                      ? "justify-end"
                      : "justify-start"
                  }
                `}
              >
                <div
                  className={`
                    max-w-[90%]
                    sm:max-w-[75%]
                    lg:max-w-[70%]
                    rounded-2xl
                    px-4
                    py-3
                    text-sm
                    leading-6
                    break-words
                    ${
                      msg.role === "user"
                        ? "bg-gray-100 text-gray-950 rounded-br-md"
                        : "bg-gray-900 border border-gray-800 text-gray-300 rounded-bl-md"
                    }
                  `}
                >
                  {msg.content}
                </div>
              </div>
            ))}

          </div>
        </div>

      </main>

      <footer
        className="
          shrink-0
          border-t
          border-gray-800
          bg-gray-950
          px-4
          py-3
          sm:px-6
          sm:py-4
        "
      >
        <div className="mx-auto w-full max-w-4xl">

          <div
            className="
              flex
              flex-col
              gap-2
              sm:flex-row
              sm:items-center
              sm:gap-4
            "
          >

            <button
              type="button"
              onClick={() => navigate("/")}
              className="
                shrink-0
                self-start
                sm:self-auto
                rounded-lg
                border
                border-red-900/50
                bg-red-950/40
                px-3
                py-2
                sm:px-4
                sm:py-2.5
                text-xs
                sm:text-sm
                font-medium
                text-red-400
                transition
                duration-200
                hover:bg-red-900/40
                hover:text-red-300
                cursor-pointer
              "
            >
              Terminate session
            </button>

            <div
              className="
                flex
                w-full
                flex-1
                items-center
                gap-2
                rounded-xl
                sm:rounded-2xl
                border
                border-gray-800
                bg-gray-900
                p-1.5
                sm:p-2
                focus-within:border-gray-700
              "
            >

              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    handleSend();
                  }
                }}
                placeholder="Ask anything about this video..."
                className="
                  min-w-0
                  flex-1
                  bg-transparent
                  px-2
                  sm:px-3
                  py-2
                  text-sm
                  text-white
                  placeholder:text-gray-600
                  outline-none
                "
              />

              <button
                type="button"
                onClick={handleSend}
                disabled={!message.trim()}
                className="
                  flex
                  h-8
                  w-8
                  sm:h-9
                  sm:w-9
                  shrink-0
                  items-center
                  justify-center
                  rounded-lg
                  sm:rounded-xl
                  bg-gray-100
                  text-gray-950
                  transition
                  hover:bg-white
                  cursor-pointer
                  disabled:cursor-not-allowed
                  disabled:opacity-30
                "
              >
                →
              </button>

            </div>
          </div>

          <p
            className="
              mt-2
              text-center
              text-[10px]
              sm:text-[11px]
              text-gray-700
            "
          >
            Ask questions about the content of your video
          </p>

        </div>
      </footer>

    </div>
  );
}