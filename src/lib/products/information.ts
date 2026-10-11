export const informationFields = [
  ['handmadeDetails', 'Handmade Details'], ['materialsUsed', 'Materials Used'],
  ['sizeDimensions', 'Size & Dimensions'], ['processingTime', 'Processing Time'],
  ['careInstructions', 'Care Instructions'], ['shippingDelivery', 'Shipping & Delivery'],
] as const;
export type InformationKey = typeof informationFields[number][0];
export type ProductInformation = Partial<Record<InformationKey, string | null>>;
export const INFORMATION_LIMIT = 5000;
export function informationValues(source: ProductInformation): ProductInformation {
  return Object.fromEntries(informationFields.map(([key]) => [key, source[key] ?? '']));
}
export function validInformation(value: ProductInformation): boolean {
  return informationFields.every(([key]) => (value[key]?.length ?? 0) <= INFORMATION_LIMIT);
}
