import type React from "react"
import "./globals.css"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import { ThemeProvider } from "@/components/theme-provider"
import Script from "next/script"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Atlas - Transform Your Online Presence",
  description: "Create stunning, interactive websites that captivate your audience and drive engagement.",
    generator: 'v0.dev'
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider attribute="class" defaultTheme="light" enableSystem disableTransitionOnChange>
          {children}
        </ThemeProvider>

        {/* Place for inline scripts */}
        <Script id="inline-script">
          {`
            // This is where you can add inline JavaScript
            document.addEventListener('DOMContentLoaded', function() {
              const updateButton = document.getElementById('demo-button-1');
              const resetButton = document.getElementById('demo-button-2');
              const contentArea = document.getElementById('dynamic-content');
              
              if (updateButton && resetButton && contentArea) {
                // Update content when button is clicked
                updateButton.addEventListener('click', function() {
                  contentArea.innerHTML = \`
                    <div class="text-center">
                      <h4 class="text-xl font-bold text-indigo-600 mb-2">
                        Dynamic Content Updated!
                      </h4>
                      <p class="text-gray-700">
                        This content was inserted using JavaScript at 
                        \${new Date().toLocaleTimeString()}
                      </p>
                      <div class="mt-4 flex justify-center">
                        <span class="inline-flex items-center px-3 py-1 rounded-full 
                        text-sm font-medium bg-green-100 text-green-800">
                          Success
                        </span>
                      </div>
                    </div>
                  \`;
                });
                
                // Reset the demo
                resetButton.addEventListener('click', function() {
                  contentArea.innerHTML = '<p class="text-gray-500 text-center">This area can be dynamically updated with your JavaScript code.</p>';
                });
              }
            });
          `}
        </Script>
      </body>
    </html>
  )
}



import './globals.css'