// Local lab only: no uploads, identifiers, cookies or field analytics.
(() => {
  const marker = document.createElement('meta');
  marker.name = 'sulocraft-lab-metrics';
  document.head.append(marker);
  const metrics = { lcpMs: null, cls: 0, maxInteractionMs: null, longTaskMs: 0, supported: PerformanceObserver.supportedEntryTypes };
  const publish = () => { marker.content = JSON.stringify(metrics); };
  let sessionStart = 0, sessionEnd = 0, sessionValue = 0;
  const observe = (type, callback, extra = {}) => {
    if (!metrics.supported.includes(type)) return;
    new PerformanceObserver(list => { callback(list.getEntries()); publish(); }).observe({ type, buffered: true, ...extra });
  };
  observe('largest-contentful-paint', entries => { metrics.lcpMs = entries.at(-1).startTime; });
  observe('layout-shift', entries => entries.forEach(entry => {
    if (entry.hadRecentInput) return;
    if (entry.startTime - sessionEnd > 1000 || entry.startTime - sessionStart > 5000) { sessionStart = entry.startTime; sessionValue = 0; }
    sessionEnd = entry.startTime;
    sessionValue += entry.value;
    metrics.cls = Math.max(metrics.cls, sessionValue);
  }));
  observe('event', entries => entries.forEach(entry => {
    if (entry.interactionId) metrics.maxInteractionMs = Math.max(metrics.maxInteractionMs ?? 0, entry.duration);
  }), { durationThreshold: 16 });
  observe('longtask', entries => entries.forEach(entry => { metrics.longTaskMs += entry.duration; }));
  publish();
})();
