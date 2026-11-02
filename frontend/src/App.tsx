import {useEffect,useState} from 'react';
const API=import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
type Obs={region:string;month:string;cpi:number;base_year:string;source_url:string;publication_date:string};
type CompareResult={adjusted_amount:number;difference:number;earlier:Obs;later:Obs};
const fields=['rent','food','transport','utilities','other'] as const;
type Field=typeof fields[number];
const money=(n:number)=>new Intl.NumberFormat('en-PH',{style:'currency',currency:'PHP'}).format(n);
export default function App(){
 const [income,setIncome]=useState('25000');
 const [costs,setCosts]=useState<Record<Field,string>>({rent:'5000',food:'6000',transport:'2500',utilities:'2000',other:'1500'});
 const [budget,setBudget]=useState<{remaining:number;total_expenses:number;expense_ratio:number|null}|null>(null);
 const [observations,setObservations]=useState<Obs[]>([]);
 const [earlier,setEarlier]=useState('');const [later,setLater]=useState('');
 const [amount,setAmount]=useState('25000');const [comparison,setComparison]=useState<CompareResult|null>(null);
 const [error,setError]=useState('');
 useEffect(()=>{fetch(`${API}/cpi/observations`).then(r=>r.json()).then(j=>setObservations(j.observations||[])).catch(()=>{});},[]);
 async function post(path:string,payload:object){const r=await fetch(`${API}${path}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});if(!r.ok)throw new Error((await r.text()).slice(0,200));return r.json();}
 async function calcBudget(){setError('');try{const inputs=[income,...fields.map(f=>costs[f])];if(inputs.some(x=>x.trim()===''||!Number.isFinite(Number(x))||Number(x)<0))throw Error('Please enter zero or greater in every field.');setBudget(await post('/budget',{income:Number(income),...Object.fromEntries(fields.map(f=>[f,Number(costs[f])]))}));}catch(e){setBudget(null);setError(String(e));}}
 async function calcCPI(){setError('');try{setComparison(await post('/cpi/compare',{amount:Number(amount),region:'Philippines',earlier_month:earlier,later_month:later}));}catch(e){setComparison(null);setError(String(e));}}
 return <main><header><span className="tag">PHILIPPINE PERSONAL FINANCE · EDUCATIONAL</span><h1>Kaya Pa Ba? PH</h1><p>Check your budget and explore how prices change over time.</p></header>
 <section><h2>Monthly budget</h2><label>Take-home income (PHP)<input type="number" min="0" value={income} onChange={e=>setIncome(e.target.value)}/></label><div className="grid">{fields.map(f=><label key={f}>{f.charAt(0).toUpperCase()+f.slice(1)}<input type="number" min="0" value={costs[f]} onChange={e=>setCosts({...costs,[f]:e.target.value})}/></label>)}</div><button onClick={calcBudget}>Calculate budget</button>{budget&&<div className="result" aria-live="polite"><p>Total expenses: <strong>{money(budget.total_expenses)}</strong></p><p>Remaining: <strong>{money(budget.remaining)}</strong></p><p>Share spent: <strong>{budget.expense_ratio===null?'Not available':(budget.expense_ratio*100).toFixed(1)+'%'}</strong></p></div>}</section>
 <section><h2>Inflation purchasing-power comparison</h2><p>Choose two months from the same verified PSA CPI series.</p>{observations.length<2?<p className="note">No verified CPI observations loaded yet. Follow the guide to download and import official PSA CPI index values. Budget tool works independently.</p>:<><label>Earlier month<select value={earlier} onChange={e=>setEarlier(e.target.value)}><option value="">Select month</option>{observations.map(o=><option key={o.month} value={o.month}>{o.month}</option>)}</select></label><label>Later month<select value={later} onChange={e=>setLater(e.target.value)}><option value="">Select month</option>{observations.map(o=><option key={o.month} value={o.month}>{o.month}</option>)}</select></label><label>Earlier monthly amount<input type="number" min="0" value={amount} onChange={e=>setAmount(e.target.value)}/></label><button onClick={calcCPI} disabled={!earlier||!later||!amount||Number(amount)<0}>Compare purchasing power</button>{comparison&&<div className="result" aria-live="polite"><p>Equivalent later amount: <strong>{money(comparison.adjusted_amount)}</strong></p><p>Change: {money(comparison.difference)}</p><small>Source: <a href={comparison.later.source_url} target="_blank" rel="noreferrer">PSA CPI table</a> · {comparison.earlier.month} to {comparison.later.month} · base year {comparison.later.base_year} · release {comparison.later.publication_date}</small></div>}</>}</section>
 {error&&<p role="alert" className="error">{error}</p>}<footer>Educational estimates only. CPI does not measure every person's actual household spending. We do not save your budget entries.</footer></main>;
}

