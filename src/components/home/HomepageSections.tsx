import type { Product } from '../../data/products';
import type { HomepageSection } from '../../lib/api/storefront';
import CategoryGrid from './CategoryGrid';
import ImageTextSection from './ImageTextSection';
import ProductGrid from './ProductGrid';
import PromoBanner from './PromoBanner';
import ReviewSection from './ReviewSection';

interface HomepageSectionsProps {
  sections: HomepageSection[];
  wishlist: number[];
  onNavigate: (url: string) => void;
  onAddToCart: (product: Product) => void;
  onToggleWishlist: (product: Product) => void;
  onProductClick: (product: Product) => void;
}

export default function HomepageSections(props: HomepageSectionsProps) {
  const orderedSections = [...props.sections].filter(section => section.enabled).sort((a, b) => a.order - b.order);
  return <>{orderedSections.map(section => {
    switch (section.type) {
      case 'category_grid': return <CategoryGrid key={section.id} section={section} onNavigate={props.onNavigate} />;
      case 'product_collection': return <ProductGrid key={section.id} section={section} wishlist={props.wishlist} onAddToCart={props.onAddToCart} onToggleWishlist={props.onToggleWishlist} onProductClick={props.onProductClick} />;
      case 'promo_banner': return <PromoBanner key={section.id} section={section} onNavigate={props.onNavigate} />;
      case 'review_section': return <ReviewSection key={section.id} section={section} />;
      case 'image_text': return <ImageTextSection key={section.id} section={section} onNavigate={props.onNavigate} />;
      default: return null;
    }
  })}</>;
}
