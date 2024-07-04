import Link from 'next/link'
import { buttonVariants } from "@/components/ui/button"

export default function Header() {
    return (
        <div>
            <div className="px-8 pt-4 bg-gradient-to-b from-emerald-300">
            {/* Top Navigation */}
            <div className="flex items-center h-20">
                <div className="flex-grow px-4">
                    <h1 className="text-2xl font-bold text-primary">sheetfreak</h1>
                </div>
                <div className="space-x-2">
                    <Link href="/login" className={buttonVariants({ variant: "default" })}>Login</Link>
                    <Link href="/getstarted" className={buttonVariants({ variant: "default" })}>Sign up</Link>
                </div>
            </div>

            {/* Spreadsheet Toolbar with Navigation Links */}
            <div className="flex items-center pb-4 space-x-2">
                <Link href="/" className={buttonVariants({ variant: "default" })}>Features</Link>
                <Link href="/pricing" className={buttonVariants({ variant: "default" })}>Pricing</Link>
                <Link href="/try" className={buttonVariants({ variant: "default" })}>Try</Link>
            </div>
            </div>
            <hr></hr>
        </div>
    )
}
