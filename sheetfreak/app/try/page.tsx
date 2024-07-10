'use client';
import { ChangeEvent, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import Header from "@/components/ui/Header"

export default function Try() {
  const [url, setUrl] = useState('')
  const [isValidUrl, setIsValidUrl] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const router = useRouter()
  const [invalidMessage, setInvalidMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleUrlChange = (e: ChangeEvent<HTMLInputElement>) => {
    const inputUrl = e.target.value
    setUrl(inputUrl)
    
    const isValid = inputUrl.startsWith('https://docs.google.com/spreadsheets/')
    setIsValidUrl(isValid)
  }

  async function onSubmit() {
    setIsLoading(true)
    if (isValidUrl) {
      const res = await fetch('/api/getfreaky', {
        method: 'POST',
        body: JSON.stringify({
          user_url: url,
        })
      })
      const result = await res.json()
      if (result.data.startsWith("Please") || result.data.includes(("Error"))) {
        setInvalidMessage(result.data)
        setIsLoading(false)
      } else {
        router.push(`/act?link=${encodeURIComponent(result.data)}`)
      }
    } else if (file) {
      const formData = new FormData()
      formData.append('file', file)
      
      const res = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      })
      
      const result = await res.json()
      if (result.data.includes("Error")) {
        setInvalidMessage(result.data)
        setIsLoading(false)
      } else {
        router.push(`/act?link=${encodeURIComponent(result.data)}`)
      }
    } else {
      setInvalidMessage("Please enter a valid Google Sheets share link or upload an .xlsx/.csv file!")
      setIsLoading(false)
    }
  }

  return (
    <div>
      <Header />
      <div className="pt-6 pl-10 space-y-4 pr-10">
        <h1 className="px-2">Try sheetfreak on a Google Sheets share link or upload a .xlsx or .csv file!</h1>
        <Input
          type="text"
          value={url}
          onChange={handleUrlChange}
          placeholder="https://docs.google.com/spreadsheets/"
        />
        <Input
          type="file"
          accept=".xlsx,.csv"
          className="w-fit"
        />
        <Button onClick={onSubmit}>
          {isLoading ? <LoadingSpinner /> : 'Get freaky!'}
        </Button>
        <p>{invalidMessage}</p>
      </div>
    </div>
  )
}