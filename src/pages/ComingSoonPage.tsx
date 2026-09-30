export default function ComingSoonPage() {
  return (
    <main className="min-h-screen bg-[#FAF7F2] px-6 py-10 text-[#2C1810]">
      <div className="mx-auto flex min-h-[calc(100vh-5rem)] max-w-4xl flex-col items-center justify-center text-center">
        <div className="mb-8 flex h-16 w-16 items-center justify-center rounded-full bg-[#F2C4CE] text-3xl" aria-hidden="true">🧶</div>
        <p className="mb-5 text-xs font-bold uppercase tracking-[0.25em] text-[#C4622D]">Handmade in India</p>
        <h1 className="max-w-3xl text-5xl font-medium leading-tight md:text-7xl" style={{ fontFamily: 'var(--font-serif)' }}>Something beautiful is being stitched together.</h1>
        <p className="mt-7 max-w-xl text-lg leading-relaxed text-[#5C3D2E]">Sulocraft is bringing thoughtful handmade crochet gifts, flowers, décor, and keepsakes to your doorstep.</p>
        <div className="mt-10 rounded-2xl border border-[#EDE4D0] bg-white px-7 py-5 text-sm text-[#8B6B4A] shadow-sm">We are preparing our first collection. Please visit again soon.</div>
        <p className="mt-12 text-sm text-[#8B6B4A]">© 2026 Sulocraft · Made with care in India</p>
      </div>
    </main>
  );
}
