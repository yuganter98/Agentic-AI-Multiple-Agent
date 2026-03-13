import { ChatWindow } from "@/components/ChatWindow";

export default function Home() {
  return (
    <main className="relative min-h-screen w-full flex flex-col selection:bg-blue-500/30 overflow-hidden bg-[#030303]">
      
      {/* Decorative Animated Background */}
      <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-blue-900/20 blur-[120px] animate-blob"></div>
        <div className="absolute top-[20%] right-[-10%] w-[35%] h-[40%] rounded-full bg-indigo-900/20 blur-[120px] animate-blob animation-delay-2000"></div>
        <div className="absolute bottom-[-10%] left-[20%] w-[50%] h-[40%] rounded-full bg-violet-900/10 blur-[120px] animate-blob animation-delay-4000"></div>
        
        {/* Noise overlay for premium texture */}
        <div className="absolute inset-0 opacity-[0.015] mix-blend-overlay pointer-events-none" style={{ backgroundImage: 'url("data:image/svg+xml,%3Csvg viewBox=%220 0 200 200%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noiseFilter%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.65%22 numOctaves=%223%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noiseFilter)%22/%3E%3C/svg%3E")' }}></div>
      </div>

      <div className="relative z-10 flex-1 flex flex-col items-center justify-center">
        <ChatWindow />
      </div>

    </main>
  );
}
