export function setMeta(selector: string, attributes: Record<string, string>) {
  const matches = document.head.querySelectorAll<HTMLMetaElement>(selector);
  let element = matches[0];
  Array.from(matches).slice(1).forEach(node => node.remove());
  if (!element) { element = document.createElement('meta'); document.head.appendChild(element); }
  Object.entries(attributes).forEach(([name, value]) => element!.setAttribute(name, value));
}

export function removeMeta(selector: string) { document.head.querySelectorAll(selector).forEach(node => node.remove()); }

export function setSchema(id: string, value?: object) {
  document.getElementById(id)?.remove();
  if (!value) return;
  const script = document.createElement('script');
  script.id = id;
  script.type = 'application/ld+json';
  script.text = JSON.stringify(value).replace(/</g, '\\u003c');
  document.head.appendChild(script);
}

export function setLink(rel: string, attributes: Record<string, string>) {
  const selector = `link[rel="${rel}"]${attributes.hreflang ? `[hreflang="${attributes.hreflang}"]` : ''}`;
  const matches = document.head.querySelectorAll<HTMLLinkElement>(selector);
  let element = matches[0];
  Array.from(matches).slice(1).forEach(node => node.remove());
  if (!element) {
    element = document.createElement('link');
    element.rel = rel;
    document.head.appendChild(element);
  }
  Object.entries(attributes).forEach(([name, value]) => element!.setAttribute(name, value));
}

