export const performance = globalThis.performance;
export function performanceNow(): number { return performance.now(); }
export function monitorEventLoopDelay() { return { enable:()=>{},disable:()=>{},mean:()=>0 }; }
export function createHistogram() { return {}; }
