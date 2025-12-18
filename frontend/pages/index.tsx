import Head from 'next/head'
import ChatBox from '@/components/ChatBox'

export default function Home() {
  return (
    <>
      <Head>
        <title>AI Product Assistant | Kyocera-Unimerco</title>
        <meta name="description" content="Next-generation AI-powered product search for industrial tools" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <main className="min-h-screen bg-gray-900 relative overflow-hidden flex items-center justify-center p-4">
        {/* Chat Interface - Centered Widget */}
        <div className="relative z-10 w-full max-w-2xl">
          <ChatBox />
        </div>
      </main>
    </>
  )
}

