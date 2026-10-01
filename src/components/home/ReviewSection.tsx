import { StarIcon } from '../Icons';
import type { ReviewSectionData } from '../../lib/api/storefront';

export default function ReviewSection({ section }: { section: ReviewSectionData }) {
  return <section className="mx-auto max-w-7xl px-4 py-14 sm:py-16"><h2 className="text-center text-4xl font-medium text-[#2C1810]" style={{ fontFamily: 'var(--font-serif)' }}>{section.title}</h2><div className="mt-8 grid gap-5 md:mt-10 md:grid-cols-3">{section.reviews.map(review => <article key={review.id} className="rounded-2xl border border-[#EDE4D0] bg-white p-6"><div className="flex gap-1" aria-label={`${review.rating} out of 5 stars`}>{Array.from({ length: review.rating }, (_, index) => <StarIcon key={index} size={14} className="text-[#C4622D]" />)}</div><blockquote className="mt-4 text-[#5C3D2E]">“{review.text}”</blockquote><p className="mt-4 text-sm font-semibold text-[#2C1810]">{review.authorName}{review.location ? ` · ${review.location}` : ''}</p></article>)}</div></section>;
}
