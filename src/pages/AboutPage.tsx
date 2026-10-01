import { ArrowRightIcon, ThreadCurve, FlowerDecor } from '../components/Icons';

interface AboutPageProps {
  onNavigate: (page: 'home' | 'shop' | 'product' | 'cart' | 'wishlist' | 'checkout' | 'about') => void;
}

export default function AboutPage({ onNavigate }: AboutPageProps) {
  return (
    <div className="min-h-screen bg-[#FAF7F2] pt-28">
      {/* Hero */}
      <section className="relative py-20 px-4 overflow-hidden" style={{ background: 'linear-gradient(135deg, #FAF7F2 0%, #F5E8D5 100%)' }}>
        <div className="absolute top-10 right-10 opacity-10">
          <FlowerDecor size={200} color="#C4622D" />
        </div>
        <div className="max-w-4xl mx-auto text-center relative">
          <p className="text-xs text-[#C4622D] font-semibold tracking-widest uppercase mb-4">Our Story</p>
          <h1 className="text-5xl lg:text-6xl font-medium text-[#2C1810] mb-6" style={{ fontFamily: 'var(--font-serif)' }}>
            Made from a<br /><em>Love for Making</em>
          </h1>
          <div className="flex justify-center mb-6">
            <ThreadCurve width={200} color="#C4622D" opacity={0.5} />
          </div>
          <p className="text-[#5C3D2E] text-lg leading-relaxed max-w-2xl mx-auto">
            Named after Anupama's mother, Sulochana, Sulocraft carries a family story that began with a grandmother, a crochet hook, and yarn reclaimed from an old sweater.
          </p>
        </div>
      </section>

      {/* Our Story */}
      <section className="py-20 px-4 bg-white">
        <div className="max-w-6xl mx-auto grid lg:grid-cols-2 gap-16 items-center">
          <div>
            <img
              src="https://images.unsplash.com/photo-1632649027900-389e810204e6?w=700&h=800&fit=crop&auto=format"
              alt="Artisan crocheting"
              className="rounded-3xl w-full"
              style={{ aspectRatio: '7/8', objectFit: 'cover' }}
            />
          </div>
          <div>
            <p className="text-xs text-[#C4622D] font-semibold tracking-widest uppercase mb-4">The Story Behind Sulocraft</p>
            <h2 className="text-4xl font-medium text-[#2C1810] mb-6" style={{ fontFamily: 'var(--font-serif)' }}>
              One Chain at a Time
            </h2>
            <div className="space-y-4 text-[#5C3D2E] leading-relaxed">
              <p>
                Sulocraft is named after my mother, Sulochana. But my love for crochet began much earlier—with my grandmother.
              </p>
              <p>
                When I was around six, seven, or maybe eight years old, winter afternoons meant sitting beside my grandmother under the warm sun, near a coconut tree. She loved crochet, and those little afternoons became my first introduction to it.
              </p>
              <p>
                My grandma bought me a crochet hook and gave me yarn reused from one of my father's old sweaters. Every now and then, she would offer a tip and tell beautiful stories while I learned—one chain, one stitch, one little discovery at a time.
              </p>
              <p>
                I was also inspired by a girl in our neighbourhood who made beautiful crochet pieces. Watching her made me want to try even more, so I practised—mostly on my own. I did not know what stitches were supposed to look like, how many belonged in a row, or what I was actually making. I simply kept trying.
              </p>
              <p>
                Some of those early creations were gloriously disfigured. One was supposed to be a bird. Somehow, I made it anyway, and that little crochet bird is still hanging at my aunt's house all these years later.
              </p>
              <p>
                Years later, when I finally had access to crochet hooks, yarn, and all the colours I could imagine, I realised the possibilities were infinite. What began beside my grandmother slowly became a love for creating things with my own hands.
              </p>
              <p className="font-medium text-[#2C1810]">
                And that is where Sulocraft begins: a little bit of my grandmother, a little bit of my mother, and a little bit of that curious girl who kept making wonderfully crooked things.
              </p>
            </div>
            <p className="mt-8 font-semibold text-[#C4622D]" style={{ fontFamily: 'var(--font-serif)' }}>— Anupama Sharma</p>
          </div>
        </div>
      </section>

      {/* Why Crochet */}
      <section className="py-20 px-4" style={{ background: '#FAF7F2' }}>
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-14">
            <p className="text-xs text-[#C4622D] font-semibold tracking-widest uppercase mb-3">Our Medium</p>
            <h2 className="text-4xl font-medium text-[#2C1810]" style={{ fontFamily: 'var(--font-serif)' }}>Why Crochet?</h2>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { icon: '🌿', title: 'Sustainable by Nature', desc: 'Crochet uses minimal tools — just a hook and yarn. No machines, no factories, no mass production. What remains is something made slowly, with care.' },
              { icon: '✋', title: 'Human by Design', desc: 'Every piece has fingerprints — not literally, but in the tiny variations that come from being made by a person rather than a machine. That\'s not imperfection; that\'s character.' },
              { icon: '🪡', title: 'Rooted in Indian Craft', desc: 'Textile arts have always been central to Indian culture. We carry that tradition forward in a contemporary, accessible way — bringing it to new generations and new occasions.' },
            ].map(({ icon, title, desc }) => (
              <div key={title} className="bg-white rounded-2xl p-8 border border-[#EDE4D0]" style={{ boxShadow: '0 2px 12px rgba(44,24,16,0.05)' }}>
                <div className="text-4xl mb-4">{icon}</div>
                <h3 className="text-xl font-medium text-[#2C1810] mb-3" style={{ fontFamily: 'var(--font-serif)' }}>{title}</h3>
                <p className="text-[#5C3D2E] text-sm leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Process */}
      <section className="py-20 px-4 bg-white">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-14">
            <p className="text-xs text-[#C4622D] font-semibold tracking-widest uppercase mb-3">How We Work</p>
            <h2 className="text-4xl font-medium text-[#2C1810]" style={{ fontFamily: 'var(--font-serif)' }}>The Handmade Process</h2>
            <p className="text-[#8B6B4A] mt-3 max-w-xl mx-auto">Each creation moves through six loving stages before it reaches you</p>
          </div>
          <div className="grid md:grid-cols-2 gap-6">
            {[
              { step: '01', title: 'Inspiration & Design', desc: 'Every piece starts with a sketch — either from a customer\'s idea or our own creative process. We draw, revise, and imagine before a single loop of yarn is picked up.', img: 'photo-1618574760337-2750f6251d20' },
              { step: '02', title: 'Yarn Selection', desc: 'We source premium cotton and wool yarns from trusted Indian suppliers. Every colour you see in our collection has been hand-tested for quality and wash-fastness.', img: 'photo-1550376026-7375b92bb318' },
              { step: '03', title: 'Hand Crocheting', desc: 'This is the heart of everything. Each stitch is placed by hand, using traditional crochet hooks. Depending on the piece, creation can take anywhere from 2 hours to 3 days.', img: 'photo-1632649027900-389e810204e6' },
              { step: '04', title: 'Finishing & Quality', desc: 'Loose ends are woven in. Shapes are blocked. Every piece is inspected against our quality standards before it moves forward — anything that doesn\'t meet them is redone.', img: 'photo-1519412849983-957822373d02' },
              { step: '05', title: 'Eco Packaging', desc: 'We pack every order in tissue paper, placed in our signature kraft boxes tied with ribbon. All packaging is 100% recyclable and reusable.', img: 'photo-1608825154649-2e9bb4cd4211' },
              { step: '06', title: 'Delivered with Love', desc: 'A handwritten note accompanies every order. Not a printed one — an actual handwritten card from the artisan who made your piece. Because some things shouldn\'t be automated.', img: 'photo-1646182504823-a02b768e28b5' },
            ].map(({ step, title, desc, img }) => (
              <div key={step} className="flex gap-5 p-6 rounded-2xl border border-[#EDE4D0] hover:border-[#C4622D]/30 transition-colors">
                <img
                  src={`https://images.unsplash.com/${img}?w=120&h=120&fit=crop&auto=format`}
                  alt={title}
                  className="w-20 h-20 rounded-xl object-cover bg-[#F5EDE0] shrink-0"
                />
                <div>
                  <span className="text-xs text-[#C4622D]/50 font-bold">{step}</span>
                  <h3 className="font-semibold text-[#2C1810] mb-1" style={{ fontFamily: 'var(--font-serif)' }}>{title}</h3>
                  <p className="text-sm text-[#5C3D2E] leading-relaxed">{desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Founder */}
      <section className="py-20 px-4" style={{ background: 'linear-gradient(135deg, #2C1810 0%, #5C3D2E 100%)' }}>
        <div className="max-w-3xl mx-auto text-center">
          <p className="text-[#F2C4CE] text-xs font-semibold tracking-widest uppercase mb-3">From the Founder</p>
          <h2 className="text-4xl font-medium text-white mb-5" style={{ fontFamily: 'var(--font-serif)' }}>Made with Memory and Possibility</h2>
          <p className="text-white/70 text-lg leading-relaxed max-w-2xl mx-auto">
            “I may not have known what I was doing back then, but I think that is where something important began. Now, one stitch at a time, I get to make something new.”
          </p>
          <p className="mt-7 text-[#F2C4CE] font-semibold">Anupama Sharma</p>
          <p className="mt-1 text-white/50 text-sm">Founder, Sulocraft</p>
        </div>
      </section>

      {/* Sustainability */}
      <section className="py-20 px-4 bg-white">
        <div className="max-w-5xl mx-auto grid lg:grid-cols-2 gap-16 items-center">
          <div>
            <p className="text-xs text-[#8FAF8C] font-semibold tracking-widest uppercase mb-4">Our Commitment</p>
            <h2 className="text-4xl font-medium text-[#2C1810] mb-6" style={{ fontFamily: 'var(--font-serif)' }}>
              Handmade is<br />Sustainable by Default
            </h2>
            <div className="space-y-4 text-[#5C3D2E]">
              <p>Crochet is made with simple tools: a hook, yarn, patient hands, and time. Each Sulocraft piece is created through that direct, human process.</p>
              <p>We choose materials and packaging thoughtfully, and we will publish specific sourcing and sustainability commitments only when we can verify them.</p>
              <p>As Sulocraft grows, the same care that shaped Anupama's first stitches will guide how every product is designed, made, and sent.</p>
            </div>
          </div>
          <div className="relative">
            <img
              src="https://images.unsplash.com/photo-1519412849983-957822373d02?w=700&h=800&fit=crop&auto=format"
              alt="Artisan at work"
              className="rounded-3xl w-full"
              style={{ aspectRatio: '7/8', objectFit: 'cover' }}
            />
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4 text-center" style={{ background: '#FAF7F2' }}>
        <p className="text-xs text-[#C4622D] font-semibold tracking-widest uppercase mb-4">Ready to explore?</p>
        <h2 className="text-4xl font-medium text-[#2C1810] mb-6" style={{ fontFamily: 'var(--font-serif)' }}>
          Find Something Made for You
        </h2>
        <p className="text-[#8B6B4A] mb-8 max-w-md mx-auto">
          Browse our full collection or tell us about something custom — we'd love to make it for you.
        </p>
        <div className="flex flex-wrap gap-4 justify-center">
          <button onClick={() => onNavigate('shop')} className="px-8 py-4 bg-[#C4622D] text-white rounded-full font-semibold hover:bg-[#D4795A] transition-all flex items-center gap-2">
            Shop Collection <ArrowRightIcon size={18} />
          </button>
          <button className="px-8 py-4 border-2 border-[#2C1810] text-[#2C1810] rounded-full font-semibold hover:bg-[#2C1810] hover:text-white transition-all">
            Custom Order
          </button>
        </div>
      </section>
    </div>
  );
}
