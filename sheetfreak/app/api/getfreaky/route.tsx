import { NextResponse } from "next/server"
import axios from 'axios'

export const maxDuration = 60

export async function POST(req: Request) {
    try {
        const body = await req.json()
        const user_url = body.user_url
        console.log("API received")
        console.log(user_url)

        if (process.env.INGEST_API_ENDPOINT) {
            const response = await axios.post(process.env.INGEST_API_ENDPOINT, {
                google_sheets_link: user_url,
            }, {
                headers: {
                    'Authorization': `Bearer ${process.env.SHEETFREAK_API_KEY}`
                }
            })

            console.log("Received status: ", response.status)
            console.log("Response data: ", response.data)
            return NextResponse.json({ data: response.data }, { status: 200 })
        } else {
            return NextResponse.json({ data: "Error" }, { status: 500 })
        }
        
    } catch(err) {
        console.error("Error details:", err)
        return NextResponse.json({ data: "Error" }, { status: 500 })
    }
}