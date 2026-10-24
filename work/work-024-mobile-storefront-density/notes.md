# Notes

Baseline at430×900: Tiny Friends API section has56px top+56px bottom padding,168px header,32px header margin. Title alone80px. Adjacent section padding compounds the blank space. Screenshot from owner is mobile; desktop untouched. User requests shared configurable template, not repeated hardcoded per-section values.

Implementation: shared CSS tokens in`src/mobileDensity.css` consumed by semantic classes in all six API section templates, fallback homepage, product card information and footer. Mobile-only `<640px`; original desktop utilities retained. No backend/content changes or new package.

Local browser:430×900 screenshot section top/bottom padding16px(vs56), header79.19px(vs168), title30.95px(vs80), header gap12px(vs32). All7rendered homepage sections16pxpadding.320/390/430px no document or section horizontal overflow; real product imagery visible.1280px retains64pxsectionpadding,36pxtitle,40pxheadergap,96pxfootermargin. API data/order/visibility retained.

Verification: Docker frontend typecheck+17relevant tests passed; rebuilt/restarted frontend, API remains healthy. Footer targeted check passed(1test);18total tests passed. Native Firefox and actual phone engines not connected; viewport checks use in-app browser, not claims of device/engine validation. Screenshot:reports/mobile-430.jpg.

Completion: self-review/security disposition Pass for CSS/template-only scope; no new trust boundary. Local result ready for owner review; nothing pushed.

2026-10-19 /24.3: Fixed menu icon edge crowding by letting brand allocation shrink and preserving a16pxrowgutter. Mobile nav75→53px; actiontargets44px, logoheight38px retained.320/390/430px nooverflow, labelclearance13px; allfiveheroCTAsclearcontrols21pxat320px. Desktop nav73px/hero620px unchanged.17tests/typecheckpassed, frontendrebuilt. Self-review/securityPass for presentation-only change. Screenshot inreports/mobile-navigation-390.jpg; no push.

2026-10-20 release authorization: Owner requested commit/push of current verified changes to dev, including Work024 mobile density/navigation, Work015 header-clearance regression and Work025 configurable LAN API/media support. Existing local Docker/browser and test evidence retained; private local .env stays ignored. Deployment acceptance is separate from successful Git push.

2026-10-20 —24.4 completed locally. Desktop combined section padding128→48px; mobile32→16px, heading gaps40→16/12→8. Shared CSS tokens only; natural promo height.19tests/typecheck passed, Docker rebuilt, no overflow320/390/430/768/1280; header/hero/product frames unchanged at baseline widths. Screenshot/JSON comparison evidence in task-003. CSS-scope security/self-review Pass; no new backend work or push.

2026-10-20 —24.5 completed locally:390px category product start398→250px, shop302→218px; product frames retained.10tests/typecheck and Docker rebuild passed, responsive320–1280 and real filter/sort/remove checks recorded in task-004. No Gemini requirement, push or deployment.

2026-10-20 —24.6 complete locally: sort/breadcrumb both12px,32px strip below menu;390px Baby first product209px (another41px saved).11tests/typecheck, Docker rebuild, responsive/sort acceptance recorded. No push.

2026-10-24 — Local container recovery (Codex, Completed): database/API/frontend found exited255. Existing stack started using root .env, preserving database volume; compose completed and API /health returned ok. User requested no additional browser checks for routine restarts; further checks stopped. No application code/deployment changes.

2026-10-24 —24.8 locally complete: unified bar, no filter chips, category root retained across clear/query; shop multi-category title verified.18tests/typecheck and Docker/browser acceptance passed. Existing changes pushed fa49f78 first; new task implementation awaits review/push. No Gemini dependency.

2026-10-24 —24.9 local completion: price slider0–100000 via validated env config, Min/Max and Reset, native control reuse/no package dependency.31 unique tests passed plus typecheck; local Docker/mobile/keyboard acceptance recorded in task-008. No backend work/push.

2026-10-24 —24.10 complete locally: BabyMax1200+sort retained; Amigurumi navigation resets0–100000/9cards.26tests/typecheck, Docker rebuild/browser evidence in task-009. No push.

2026-10-24 — Owner authorized commit/push of locally verified24.8–24.10: unified catalogue header/scoped filters, configurable price range and navigation reset; test/security/browser evidence retained in exact task returns. Deployment acceptance remains separate from Git push.

2026-10-24 —24.11 complete locally: Shop/Collections footer navigation resets top; actual Shop/Gifts/Birthday/Custom Orders allscroll0.8tests/typecheck and Docker/browser acceptance passed. No push.

2026-10-24 —24.12 complete locally: login loading/form use one centered frame, no point-to-popup resize;9tests/typecheck and desktop/mobile/short geometry accepted. No real auth requests/session changes. See task-011. Nothing pushed.
