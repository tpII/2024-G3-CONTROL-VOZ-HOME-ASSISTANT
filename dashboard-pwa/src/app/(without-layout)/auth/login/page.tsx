import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import Link from "next/link";

export default function Login() {
  return (
    <section className="size-full flex justify-center items-center">
      <Card className="w-full max-w-md mx-auto bg-gray-900 border-gray-800">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold">Login</CardTitle>
          <CardDescription>
            Enter your email and password to access your account
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="m@example.com"
              className="bg-gray-900 border-gray-800"
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              className="bg-gray-900 border-gray-800"
              required
            />
          </div>
          <Link href="/auth/register" className="text-xs italic">
            Don't have an account? Register
          </Link>
        </CardContent>
        <CardFooter>
          <Button className="w-full text-white bg-pink-500 hover:bg-pink-600">
            Sign In
          </Button>
        </CardFooter>
      </Card>
    </section>
  );
}
