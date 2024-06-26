'use client';

import { ChangeEvent, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import LoadingSpinner from '@/components/ui/LoadingSpinner';

export default function Home() {
  const [url, setUrl] = useState('')
  const [isValidUrl, setIsValidUrl] = useState(false)
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
      const new_url = await res.json()
      if (new_url.data.startsWith("Please")) {
        setInvalidMessage(new_url.data)
        setIsLoading(false)
      } else {
        router.push(`/act?link=${encodeURIComponent(new_url.data)}`)
      }
      
    } else {
      setInvalidMessage("Please enter a valid Google Sheets share link and make sure it's set to 'Anyone with the link can view'!")
      setIsLoading(false)
    }
  }

  return (
    <div className="p-10 space-y-4">
      <h1 className="pb-4 pl-2 font-bold text-2xl">freakinthesheets</h1>
      <Input
        type="text"
        value={url}
        onChange={handleUrlChange}
        placeholder="https://docs.google.com/spreadsheets/"
      />
      
      <Button
        onClick={onSubmit}
      >{isLoading ? <LoadingSpinner /> : 'Get freaky!'}</Button>
      <p>{invalidMessage}</p>
    </div>
  )
}
