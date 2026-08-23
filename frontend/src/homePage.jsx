import { VidRecallLogo } from "./logo.jsx";
import { useNavigate } from "react-router-dom";

export function HomePage(){
    const navigate = useNavigate()

    return(
        <div className="min-h-screen bg-gray-950 text-white flex flex-col">
      <header onClick = {() => navigate("/")}
      className="px-4 py-5 sm:px-6 sm:py-6 lg:px-8 cursor-pointer">
        <VidRecallLogo />
      </header>

      <main className="flex-1 px-4 pb-8 sm:px-6 sm:pb-10 lg:px-8">
        <div className="w-full max-w-5xl mx-auto">
          <div className="mb-6 sm:mb-8">
            <h1
              className="
              text-2xl
              sm:text-3xl
              font-semibold
              tracking-tight
            "
            >
              What do you want to do?
            </h1>

            <p
              className="
              mt-2
              text-sm
              sm:text-base
              text-gray-400
              max-w-xl
              leading-6
            "
            >
              Turn videos into knowledge or continue a conversation.
            </p>
          </div>

          <div
            className="
            grid
            grid-cols-1
            md:grid-cols-2
            gap-4
            sm:gap-5
          "
          >
            <div
              className="
              group
              relative
              overflow-hidden
              rounded-2xl
              border
              border-gray-800
              bg-gray-900/70
              p-5
              sm:p-6
              lg:p-7
              hover:border-gray-700
              transition-all
              duration-200
            "
            >
              <div
                className="
                w-11
                h-11
                sm:w-12
                sm:h-12
                rounded-xl
                bg-white/10
                flex
                items-center
                justify-center
                mb-5
                sm:mb-6
                text-lg
                sm:text-xl
              "
              >
                ▶
              </div>

              <h2
                className="
                text-lg
                sm:text-xl
                font-semibold
              "
              >
                Process a video
              </h2>

              <p
                className="
                mt-2
                text-sm
                leading-6
                text-gray-400
                max-w-sm
              "
              >
                Paste a YouTube URL and turn the video into searchable,
                conversational knowledge.
              </p>

              <button onClick = {() => navigate("/process")}
                className="
                mt-6
                sm:mt-7
                inline-flex
                items-center
                gap-2
                px-4
                py-2
                rounded-lg
                bg-gray-800
                hover:bg-gray-700
                text-sm
                font-medium
                cursor-pointer
                transition-all
                duration-200
              "
              >
                Get started
                <span
                  className="
                  transition-transform
                  duration-200
                  group-hover:translate-x-1
                "
                >
                  →
                </span>
              </button>
            </div>

            <div
              className="
              group
              relative
              overflow-hidden
              rounded-2xl
              border
              border-gray-800
              bg-gray-900/70
              p-5
              sm:p-6
              lg:p-7
              hover:border-gray-700
              transition-all
              duration-200
            "
            >
              <div
                className="
                w-11
                h-11
                sm:w-12
                sm:h-12
                rounded-xl
                bg-white/10
                flex
                items-center
                justify-center
                mb-5
                sm:mb-6
                text-lg
                sm:text-xl
              "
              >
                💬
              </div>

              <h2
                className="
                text-lg
                sm:text-xl
                font-semibold
              "
              >
                Start a new session
              </h2>

              <p
                className="
                mt-2
                text-sm
                leading-6
                text-gray-400
                max-w-sm
              "
              >
                Choose a processed video and start asking questions about its
                content.
              </p>

               <button onClick = {() => navigate("/session")}
                className="
                mt-6
                sm:mt-7
                inline-flex
                items-center
                gap-2
                px-4
                py-2
                rounded-lg
                bg-gray-800
                hover:bg-gray-700
                text-sm
                font-medium
                cursor-pointer
                transition-all
                duration-200
              "
              >
                start chatting
                <span
                  className="
                  transition-transform
                  duration-200
                  group-hover:translate-x-1
                "
                >
                  →
                </span>
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
    )
}