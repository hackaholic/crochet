# Work 001 decisions

- Use the owner-provided Figma admin export as the design source; preserve its layout and visual language.
- Keep the existing Sulocraft routing/API architecture; admin business data must come from the backend.
- Do not treat Figma metadata or demo records as product data.
- The exported `mockData.ts` is prototype-only and must not be imported by the runtime admin screens.
- Keep Products, Inventory, Customers, and Settings clearly identified as unfinished until their screens and data contracts are implemented; do not make placeholder content look like working management tools.
- Local browser/Docker verification and owner review are acceptance gates before push or deployment.
