'use client';
import { ChangeEvent, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import LoadingSpinner from '@/components/ui/LoadingSpinner';

export default function Home() {
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

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0]
      const fileType = selectedFile.name.split('.').pop()?.toLowerCase()
      if (fileType === 'xlsx' || fileType === 'csv') {
        setFile(selectedFile)
        setInvalidMessage('')
      } else {
        setFile(null)
        setInvalidMessage('Please upload only .xlsx or .csv files.')
      }
    }
  }

  async function onSubmit() {
    setIsLoading(true)
    if (isValidUrl) {
      // TODO: try/except this call for when API call errors and doesn't return something that starts with 'Please'
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
    } else if (file) {
      const formData = new FormData()
      formData.append('file', file)
      
      const res = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      })
      
      const result = await res.json()
      if (!result.data.includes("Error")) {
        router.push(`/act?link=${encodeURIComponent(result.data)}`)
      } else {
        setInvalidMessage(result.data || 'Error uploading da file')
        setIsLoading(false)
      }
    } else {
      setInvalidMessage("Please enter a valid Google Sheets share link or upload an .xlsx/.csv file!")
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
      <Input
        type="file"
        onChange={handleFileChange}
        accept=".xlsx,.csv"
      />
      <Button onClick={onSubmit}>
        {isLoading ? <LoadingSpinner /> : 'Get freaky!'}
      </Button>
      <p>{invalidMessage}</p>
    </div>
  )
}