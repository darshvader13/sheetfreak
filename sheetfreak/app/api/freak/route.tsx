import { NextResponse } from "next/server"
import { StreamingTextResponse } from "ai"
import axios from 'axios'
import { Message } from "@/components/interfaces/interfaces"

export const maxDuration = 60

export async function POST(req: Request) {
    try {
        const body = await req.json()
        const task_prompt = body.task_prompt
        const spreadsheet_id = body.spreadsheet_id
        const messages : Message[] = body.messages
        console.log("API received")
        console.log(task_prompt)
        console.log(spreadsheet_id)
        console.log(messages)

        if (process.env.ACT_API_ENDPOINT) {
            const response = await axios.post(process.env.ACT_API_ENDPOINT, {
                task_prompt: task_prompt,
                spreadsheet_id: spreadsheet_id,
                messages: messages,
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