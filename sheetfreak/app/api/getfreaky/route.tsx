import { NextResponse } from "next/server"
import axios from 'axios'

export const maxDuration = 60

export async function POST(req: Request) {
    try {
        const body = await req.json()
        const user_url = body.user_url
        console.log("API received")
        console.log(user_url)

        //Production
        const response = await axios.post('https://sheetfreak--freakinthesheets-ingest.modal.run', {
            google_sheets_link: user_url,
        })

        //Development
        // const response = await axios.post('https://sheetfreak--freakinthesheets-ingest-dev.modal.run', {
        //     google_sheets_link: user_url,
        // })
        

        console.log("Received status: ")
        console.log(response.data)
        return NextResponse.json({ data: response.data }, { status: 200 })
    } catch(err) {
        console.log(err)
        return NextResponse.json({ data: "Error" }, { status: 500 })
    }
}