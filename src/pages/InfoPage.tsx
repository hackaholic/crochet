type InfoPageKind = 'contact' | 'shipping' | 'returns' | 'privacy' | 'terms' | 'notFound';

interface InfoPageProps {
  kind: InfoPageKind;
  onNavigate: (page: 'home' | 'shop') => void;
}

type Section = {
  title: string;
  body: string;
};

const pageContent: Record<Exclude<InfoPageKind, 'notFound'>, { eyebrow: string; title: string; intro: string; sections: Section[] }> = {
  contact: {
    eyebrow: 'We are here to help',
    title: 'Contact us',
    intro: 'Questions about a product, a custom order, or an existing purchase? Send us a note and our small team will get back to you with care.',
    sections: [
      { title: 'Order support', body: 'Please include your order number and the email or phone number used at checkout, so we can find the right details quickly.' },
      { title: 'Custom creations', body: 'Tell us what you have in mind, including the occasion, preferred size, and when you need it. We will confirm feasibility and a tailored quote before work begins.' },
      { title: 'Response time', body: 'We aim to respond within two working days. During festival seasons and custom-order peaks, a little extra time may be needed.' },
    ],
  },
  shipping: {
    eyebrow: 'Delivery with care',
    title: 'Shipping policy',
    intro: 'Every Sulocraft piece is packed to travel safely and arrive ready to gift. Final shipping choices and delivery estimates appear at checkout.',
    sections: [
      { title: 'Processing time', body: 'Ready pieces and made-to-order work can have different preparation times. The product page and checkout will show the applicable estimate before you place an order.' },
      { title: 'Delivery', body: 'We share tracking details after dispatch when they are available. Delivery estimates are provided by the delivery partner and may vary by location and season.' },
      { title: 'Shipping charges', body: 'Any delivery charge, free-shipping threshold, or express option will be clearly shown before payment. We do not add an unexpected shipping charge after an order is placed.' },
    ],
  },
  returns: {
    eyebrow: 'A fair resolution',
    title: 'Return policy',
    intro: 'Because handmade and customised pieces are personal, return eligibility depends on the item and its condition. Contact us promptly if something is not right.',
    sections: [
      { title: 'Damaged or incorrect items', body: 'Contact us with clear photos and your order details as soon as you receive the item. We will review the issue and arrange the appropriate resolution.' },
      { title: 'Custom orders', body: 'Personalised and made-to-order pieces may not be eligible for a standard return unless they arrive damaged, defective, or materially different from the confirmed order.' },
      { title: 'Before sending anything back', body: 'Please wait for return instructions from our team. This ensures your parcel reaches the right place and your request is recorded correctly.' },
    ],
  },
  privacy: {
    eyebrow: 'Your information',
    title: 'Privacy policy',
    intro: 'We use customer information only to operate the store, fulfil orders, provide support, and improve the shopping experience.',
    sections: [
      { title: 'Information we use', body: 'This can include contact details, delivery details, order information, and the information you choose to share for a custom order.' },
      { title: 'How it is used', body: 'We use it to process purchases, deliver products, answer questions, prevent misuse, and meet legal obligations. We do not sell personal information.' },
      { title: 'Your choices', body: 'You can contact us to ask about your information, update account details, or opt out of promotional communication when that feature becomes available.' },
    ],
  },
  terms: {
    eyebrow: 'Shopping with Sulocraft',
    title: 'Terms and conditions',
    intro: 'These terms set out the basic expectations for browsing, ordering, and receiving handmade items from Sulocraft.',
    sections: [
      { title: 'Handmade variation', body: 'Small variations in stitch, shape, colour, and finish are a natural part of handmade work. Product photography and descriptions will represent each piece as accurately as possible.' },
      { title: 'Orders and availability', body: 'An order is subject to product availability, confirmed pricing, and any required customisation details. We will contact you if a meaningful change is needed before fulfilment.' },
      { title: 'Intellectual property', body: 'The Sulocraft name, product photography, writing, and design are protected. Please do not reproduce them without permission.' },
    ],
  },
};

export default function InfoPage({ kind, onNavigate }: InfoPageProps) {
  if (kind === 'notFound') {
    return (
      <section className="min-h-[60vh] bg-[#FAF7F2] px-4 pt-36 pb-24 flex items-center justify-center">
        <div className="max-w-lg text-center">
          <p className="text-xs tracking-[0.2em] uppercase font-semibold text-[#C4622D] mb-4">Page not found</p>
          <h1 className="text-4xl md:text-5xl text-[#2C1810] mb-5" style={{ fontFamily: 'var(--font-serif)' }}>This stitch is missing.</h1>
          <p className="text-[#8B6B4A] leading-relaxed mb-8">The page you are looking for may have moved or may not exist yet.</p>
          <button onClick={() => onNavigate('home')} className="rounded-full bg-[#C4622D] px-7 py-3 text-sm font-semibold text-white transition-colors hover:bg-[#D4795A]">Back to home</button>
        </div>
      </section>
    );
  }

  const content = pageContent[kind];

  return (
    <section className="bg-[#FAF7F2] px-4 pt-36 pb-24">
      <div className="mx-auto max-w-3xl">
        <p className="text-xs tracking-[0.2em] uppercase font-semibold text-[#C4622D] mb-4">{content.eyebrow}</p>
        <h1 className="text-4xl md:text-5xl text-[#2C1810] mb-5" style={{ fontFamily: 'var(--font-serif)' }}>{content.title}</h1>
        <p className="max-w-2xl text-[#8B6B4A] leading-relaxed mb-12">{content.intro}</p>
        <div className="space-y-4">
          {content.sections.map(section => (
            <article key={section.title} className="rounded-2xl border border-[#EDE4D0] bg-white p-6 md:p-8">
              <h2 className="text-xl text-[#2C1810] mb-3" style={{ fontFamily: 'var(--font-serif)' }}>{section.title}</h2>
              <p className="text-sm leading-7 text-[#5C3D2E]">{section.body}</p>
            </article>
          ))}
        </div>
        <div className="mt-10 rounded-2xl bg-[#F5EDE0] p-6 text-center">
          <p className="text-sm text-[#5C3D2E] mb-4">Looking for something handmade just for you?</p>
          <button onClick={() => onNavigate('shop')} className="rounded-full border border-[#C4622D] px-6 py-2.5 text-sm font-semibold text-[#C4622D] transition-colors hover:bg-[#C4622D] hover:text-white">Explore the collection</button>
        </div>
      </div>
    </section>
  );
}
