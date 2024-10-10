import { RetryButton } from "@/components/app/retry-button";
import { WifiOff } from "lucide-react";

export default function Component() {
  return (
    <div className="flex flex-col items-center justify-center p-4 space-y-6">
      <h1 className="text-2xl font-bold text-pink-500">No Connection</h1>
      <WifiOff className="w-16 h-16 text-pink-500" />
      <p className="text-center text-gray-400 max-w-xs">
        Oops! It looks like you're offline. Please check your internet
        connection and try again.
      </p>
      <RetryButton />
    </div>
  );
}
