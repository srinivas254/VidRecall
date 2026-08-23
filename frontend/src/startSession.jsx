import { useState } from "react";

import { useNavigate } from "react-router-dom";

import { VidRecallLogo } from "./logo.jsx";

import { toast } from "react-toastify";

export function StartSession() {
  const navigate = useNavigate();

  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [loading, setLoading] = useState(false);

  const handleBeginSession = async () => {
    if (loading) return;

    setLoading(true);

    try {
      const response = await fetch(
        "http://localhost:8000/session",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            url: youtubeUrl,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail);
      }

      toast.success("session started")

      navigate("/chat", {
        state: {
          source: data.source,
          videoId: data.video_id,
        },
      });
    } catch (error) {
      toast.error(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col">

      <header
        onClick={() => navigate("/")}
        className="
          shrink-0
          cursor-pointer
          px-4
          py-5
          sm:px-6
          sm:py-6
          lg:px-8
          lg:py-7
        "
      >
        <VidRecallLogo />
      </header>

      <main
        className="
          flex-1
          flex
          items-center
          justify-center
          px-4
          py-10
          sm:px-6
          sm:py-12
          lg:px-8
          lg:py-16
        "
      >
        <div
          className="
            w-full
            max-w-xl
            sm:max-w-2xl
          "
        >

          <div className="mb-7 sm:mb-9 lg:mb-10">

            <p
              className="
                mb-3
                text-[11px]
                sm:text-xs
                font-medium
                uppercase
                tracking-[0.15em]
                text-gray-500
              "
            >
              New session
            </p>

            <h1
              className="
                text-3xl
                sm:text-4xl
                lg:text-5xl
                font-semibold
                tracking-tight
                leading-tight
              "
            >
              Talk to a
              <span className="text-gray-400">
                {" "}video.
              </span>
            </h1>

            <p
              className="
                mt-4
                max-w-xl
                text-sm
                sm:text-base
                leading-6
                text-gray-400
              "
            >
              Paste a YouTube video and ask questions about
              its content. VidRecall will turn the video into
              an interactive conversation.
            </p>

          </div>

          <div
            className="
              rounded-xl
              sm:rounded-2xl
              border
              border-gray-800
              bg-gray-900/70
              p-4
              sm:p-5
              lg:p-6
            "
          >

            <label
              htmlFor="youtube-url"
              className="
                block
                mb-3
                text-sm
                font-medium
                text-gray-300
              "
            >
              YouTube URL
            </label>

            <input
              id="youtube-url"
              type="url"
              value={youtubeUrl}
              onChange={(e) => setYoutubeUrl(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  handleBeginSession();
                }
              }}
              placeholder="https://youtube.com/watch?v=..."
              className="
                w-full
                rounded-lg
                border
                border-gray-800
                bg-gray-950
                px-3.5
                py-3
                sm:px-4
                sm:py-3.5
                text-sm
                text-white
                placeholder:text-gray-600
                outline-none
                transition
                duration-200
                focus:border-gray-600
                focus:ring-1
                focus:ring-gray-700
              "
            />

            <button
              onClick={handleBeginSession}
              type="button"
              disabled={loading}
              className="
                mt-3
                sm:mt-4
                w-full
                flex
                items-center
                justify-center
                gap-2
                rounded-lg
                bg-gray-100
                px-5
                py-3
                sm:py-3.5
                text-sm
                font-medium
                text-gray-950
                hover:bg-white
                active:bg-gray-200
                cursor-pointer
                transition-colors
                duration-200
                disabled:cursor-not-allowed
                disabled:opacity-50
              "
            >
              {loading ? "Processing..." : "Begin session"}

              {!loading && (
                <span>→</span>
              )}
            </button>

            <p
              className="
                mt-3
                text-center
                text-[11px]
                sm:text-xs
                text-gray-600
              "
            >
              Currently supports public YouTube videos.
            </p>

          </div>

          <div
            className="
              mt-5
              sm:mt-6
              flex
              items-center
              justify-center
              gap-2
              text-[11px]
              sm:text-xs
              text-gray-600
              text-center
            "
          >
            <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-gray-600" />

            <span>
              Your video stays associated with this session
            </span>
          </div>

        </div>
      </main>

    </div>
  );
}