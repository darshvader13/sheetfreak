import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from "@/components/ui/button"

export default function ChatPreview() {
    const router = useRouter()
    const chat_id = 'chat-00000000'
    const chat_title = "Sample Title"
    const chat_share_link = "https://samplesharelink.com"

    function onSubmit() {
        router.push(`/act?link=${encodeURIComponent(chat_id)}`)
    }

    return (
        <div className="">
            <h3>{chat_title}</h3>
            <Link
              href={chat_share_link}
              rel="noopener noreferrer"
              target="_blank"
              className="pl-2 underline text-blue-600 hover:text-blue-800 visited:text-purple-600">
                {chat_share_link}
            </Link>
            <Button onClick={onSubmit}>Resume</Button>
        </div>
    )
}