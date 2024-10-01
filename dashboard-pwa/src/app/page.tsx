"use client";

import { useState } from "react";
import { Lightbulb } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function Component() {
  const [isLightOn, setIsLightOn] = useState(false);

  const toggleLight = () => {
    setIsLightOn(!isLightOn);
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      <Card className="bg-gray-900 border-gray-800">
        <CardContent className="p-4">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between space-y-4 sm:space-y-0 sm:space-x-4">
            <div className="flex items-center space-x-4">
              <Button
                variant="outline"
                size="icon"
                className={`h-16 w-16 rounded-full transition-colors border-2 ${
                  isLightOn
                    ? "bg-pink-900 border-pink-500 text-pink-500"
                    : "bg-gray-800 border-gray-700 text-gray-400"
                }`}
                onClick={toggleLight}
                aria-pressed={isLightOn}
                aria-label={isLightOn ? "Turn off light" : "Turn on light"}
              >
                <Lightbulb
                  className={`h-8 w-8 ${isLightOn ? "fill-current" : ""}`}
                />
              </Button>
              <div>
                <h2 className="text-lg font-semibold text-white">Test Light</h2>
                <p className="text-sm text-gray-400">
                  {isLightOn ? "On" : "Off"}
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
