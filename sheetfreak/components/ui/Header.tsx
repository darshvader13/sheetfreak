import Link from 'next/link'
import Image from 'next/image'
import { buttonVariants } from "@/components/ui/button"

export default function Header() {
    return (
        <div>
            <div className="px-8 pt-4 bg-gradient-to-b from-emerald-300">
            {/* Top Navigation */}
            <div className="flex justify-between">
                <div className="flex items-center">
                    <Image src="/logo.png" alt="logo" height="100" width="100"/>
                    <h1 className="text-4xl font-bold text-primary">sheetfreak</h1>
                </div>
                <div className="flex space-x-2 pt-8 justify-end">
                    <Link href="/login" className={buttonVariants({ variant: "outline" })}>Login</Link>
                    <Link href="/getstarted" className={buttonVariants({ variant: "default" })}>Sign up</Link>
                </div>
            </div>

            {/* Spreadsheet Toolbar with Navigation Links */}
            <div className="flex items-center pb-4 pl-4 space-x-6">
                <Link href="/" className="text-sm font-semibold hover:underline underline-offset-4">Features</Link>
                <Link href="/pricing" className="text-sm font-semibold hover:underline underline-offset-4">Pricing</Link>
                <Link href="/try" className="text-sm font-semibold hover:underline underline-offset-4">Try</Link>
            </div>
            </div>
            <hr></hr>
        </div>
    )
}
