import { NextRequest, NextResponse } from "next/server"
import axios from 'axios'

export const maxDuration = 60

export async function POST(req: Request) {
    try {
        const formData = await req.formData()
        const file = formData.get('file') as File
        
        if (!file) {
            return NextResponse.json({ error: "No file uploaded" }, { status: 400 })
        }

        const maxSize = 10 * 1024 * 1024 // 10MB in bytes
        if (file.size > maxSize) {
            return NextResponse.json({ error: "File too large" }, { status: 400 })
        }

        const modalFormData = new FormData()
        modalFormData.append('file', file)

        console.log(modalFormData)

        const response = await axios.post('https://sheetfreak--sheetfreak-upload-dev.modal.run', modalFormData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        })
        
        console.log("Received status: ", response.status)
        console.log("Response data: ", response.data)
        return NextResponse.json({ data: response.data }, { status: 200 })
    } catch (err) {
        console.error("Error details:", err)
        if (axios.isAxiosError(err) && err.response) {
            console.error("Full error response:", JSON.stringify(err.response.data, null, 2));
            return NextResponse.json({ error: err.response.data }, { status: err.response.status })
        }
        return NextResponse.json({ error: "Internal Server Error" }, { status: 500 })
    }
}