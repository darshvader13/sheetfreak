import Link from 'next/link'
import Image from 'next/image'
import { buttonVariants } from "@/components/ui/button"

export default function Header() {
    return (
        <div>
            <div className="bg-gradient-to-b from-emerald-300 via-teal-300 p-4 sm:p-8">
                {/* Top Navigation */}
                <div className="flex flex-col space-y-2 sm:space-y-0 sm:flex-row sm:items-center sm:justify-between">
                    <div className="flex items-center space-x-2">
                        <Image src="/big logo.png" alt="logo" height="80" width="80" />
                        <h1 className="text-4xl font-bold text-primary tracking-tight"><Link href="/">sheetfreak</Link></h1>
                    </div>
                    <div className="flex space-x-2">
                        <Link href="/" className={`${buttonVariants({ variant: "outline" })} hover:bg-gradient-to-r hover:from-emerald-300 hover:to-blue-300`}>Login</Link>
                         <Link href="/" className={`${buttonVariants({ variant: "default" })} hover:bg-gradient-to-r hover:from-emerald-300 hover:to-blue-400 hover:text-black`}>Sign up</Link>
                    </div>
                </div>
                {/* Spreadsheet Toolbar with Navigation Links */}
                <div className="flex text-sm space-x-6 sm:justify-start sm:mt-6">
                    <Link href="/try" className="hover:underline underline-offset-4">Try</Link>
                    <Link href="/" className="hover:underline underline-offset-4">Features</Link>
                    <Link href="/" className="hover:underline underline-offset-4">Pricing</Link>
                </div>
            </div>
            <hr></hr>
        </div>
    )
}
