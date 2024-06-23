import { NextResponse } from "next/server"
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

        const response = await axios.post('https://kcui5--freakinthesheets-act-dev.modal.run', {
            task_prompt: task_prompt,
            sheet_id: sheet_id,
        })

        console.log("Received status: ")
        console.log(response.data)
        return NextResponse.json({ data: response.data }, { status: 200 })
    } catch(err) {
        console.log(err)
        return NextResponse.json({ data: "Error" }, { status: 500 })
    }
}