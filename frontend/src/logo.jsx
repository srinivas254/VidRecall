import {
  PlayIcon,
  ArrowPathIcon,
  SparklesIcon,
} from "@heroicons/react/24/solid";

export function VidRecallLogo({ showText = true }) {
  return (
    <div className="flex items-center gap-3">
      <div className="relative flex h-11 w-11 items-center justify-center">
        
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-blue-500 to-indigo-600 shadow-lg shadow-blue-500/30">
          <PlayIcon className="h-5 w-5 text-white" />
        </div>

        <ArrowPathIcon className="absolute -right-1 -bottom-1 h-7 w-7 text-cyan-400" />

        <SparklesIcon className="absolute -top-1 -right-1 h-4 w-4 text-purple-400" />
      </div>

      {showText && (
        <div className="text-xl font-bold tracking-tight">
          <span className="text-white">Vid</span>
          <span className="bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
            Recall
          </span>
        </div>
      )}
    </div>
  );
}