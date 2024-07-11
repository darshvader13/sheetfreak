import { NextResponse } from "next/server"
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

        if (process.env.UPLOAD_API_ENDPOINT) {
            const response = await axios.post(process.env.UPLOAD_API_ENDPOINT, modalFormData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            })
            
            console.log("Received status: ", response.status)
            console.log("Response data: ", response.data)
            return NextResponse.json({ data: response.data }, { status: 200 })
        } else {
            return NextResponse.json({ data: "Error" }, { status: 500 })
        }
    } catch (err) {
        console.error("Error details:", err)
        return NextResponse.json({ data: "Error" }, { status: 500 })
    }
}