import { NextResponse } from "next/server"
import { StreamingTextResponse } from "ai"
import axios from 'axios'

export const maxDuration = 60

export async function POST(req: Request) {
    try {
        const body = await req.json()
        const task_prompt = body.task_prompt
        const sheet_id = body.sheet_id
        console.log("API received")
        console.log(task_prompt)
        console.log(sheet_id)

        if (process.env.ACT_API_ENDPOINT) {
            const response = await axios.post(process.env.ACT_API_ENDPOINT, {
                task_prompt: task_prompt,
                sheet_id: sheet_id,
            }, {
                responseType: 'stream',
            })

            const stream = response.data
            return new StreamingTextResponse(stream)
        } else {
            return NextResponse.json({ data: "Error" }, { status: 500 })
        }
        
    } catch(err) {
        console.error("Error details:", err)
        return NextResponse.json({ data: "Error" }, { status: 500 })
    }
}