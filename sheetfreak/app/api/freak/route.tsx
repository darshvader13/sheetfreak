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

        //Production
        // const response = await axios.post('https://sheetfreak--sheetfreak-act.modal.run', {
        //     task_prompt: task_prompt,
        //     sheet_id: sheet_id,
        // }, {
        //     responseType: 'stream',
        // })

        //Development
        const response = await axios.post('https://sheetfreak--sheetfreak-act-dev.modal.run', {
            task_prompt: task_prompt,
            sheet_id: sheet_id,
        }, {
            responseType: 'stream',
        })

        const stream = response.data
        return new StreamingTextResponse(stream)

        // console.log("Received status: ")
        // console.log(response.data)
        // res.write("Starting")
        // return NextResponse.json({ data: "Starting stream" }, { status: 200 })
    } catch(err) {
        console.log(err)
        return NextResponse.json({ data: "Error" }, { status: 500 })
    }
}