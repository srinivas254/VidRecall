import { VidRecallLogo } from "./logo.jsx";
import { useNavigate } from "react-router-dom";
import { useState } from "react";
import { toast } from "react-toastify";

export function ProcessVideo() {
  const navigate = useNavigate();
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [loading, setLoading] = useState(false);

  const handleProcess = async () => {
    if (!youtubeUrl.trim()) {
      return;
    }

    try {
      setLoading(true);

      const response = await fetch("http://localhost:8000/video-process", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          url: youtubeUrl,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail);
      }

      const data = await response.json();
      toast.success(data.message);

      navigate("/");
    } catch (error) {
      console.error(error);
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
          px-4 py-5
          sm:px-6 sm:py-6
          lg:px-8 lg:py-7
          cursor-pointer
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
        pb-10
        sm:px-6
        lg:px-8
      "
      >
        <div className="w-full max-w-2xl">
          <div className="mb-8 sm:mb-10">
            <p
              className="
              mb-3
              text-sm
              font-medium
              text-gray-500
              tracking-wide
              uppercase
            "
            >
              Video processing
            </p>

            <h1
              className="
              text-3xl
              sm:text-4xl
              lg:text-5xl
              font-semibold
              tracking-tight
            "
            >
              Turn a video into
              <span className="text-gray-400"> knowledge.</span>
            </h1>

            <p
              className="
              mt-4
              text-sm
              sm:text-base
              text-gray-400
              leading-6
              max-w-xl
            "
            >
              Paste a YouTube video URL below and VidRecall will prepare it for
              an interactive conversation.
            </p>
          </div>

          <div
            className="
            rounded-2xl
            border
            border-gray-800
            bg-gray-900/70
            p-4
            sm:p-5
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

            <div
              className="
              flex
              flex-col
              sm:flex-row
              gap-3
            "
            >
              <input
                id="youtube-url"
                type="url"
                value={youtubeUrl}
                onChange={(e) => setYoutubeUrl(e.target.value)}
                placeholder="https://youtube.com/watch?v=..."
                className="
                  flex-1
                  min-w-0
                  rounded-lg
                  border
                  border-gray-800
                  bg-gray-950
                  px-4
                  py-3
                  text-sm
                  text-white
                  placeholder:text-gray-600
                  outline-none
                  transition
                  focus:border-gray-600
                  focus:ring-1
                  focus:ring-gray-700
                "
              />

              <button
                onClick={handleProcess}
                type="button"
                className="
                  shrink-0
                  rounded-lg
                  bg-gray-100
                  px-5
                  py-3
                  text-sm
                  font-medium
                  text-gray-950
                  hover:bg-white
                  active:bg-gray-200
                  cursor-pointer
                  transition-colors
                  duration-200
                "
              >
                {loading ? (
                  <span className="flex items-center gap-2">
                    <span
                      className="
                      h-4
                      w-4
                      animate-spin
                      rounded-full
                      border-2
                      border-gray-400
                      border-t-gray-950
                    "
                    />
                    Processing...
                  </span>
                ) : (
                  <>
                    Process
                    <span className="ml-2">→</span>
                  </>
                )}
              </button>
            </div>

            <p
              className="
              mt-3
              text-xs
              text-gray-600
            "
            >
              Currently supports public YouTube videos.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
