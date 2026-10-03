import {useState} from 'react'
import {useQuery,useMutation,useQueryClient} from '@tanstack/react-query'
import {Shield,LayoutDashboard,TriangleAlert,Boxes,Radio,Server,ArrowUpRight,Activity,LogOut,ChevronRight,FlaskConical} from 'lucide-react'
import {AreaChart,Area,CartesianGrid,XAxis,YAxis,Tooltip,ResponsiveContainer} from 'recharts'
import {api,date} from './api'
import {Dashboard,Incident,Service,Source,Scan} from './types'
import {Badge,Panel,ErrorBox,Loading,Empty} from './ui'
import {Services,Sources,Events} from './DataPages'
import {Images} from './Images'
import {IncidentDetail} from './IncidentDetail'

const nav=[['overview','Обзор',LayoutDashboard],['incidents','Инциденты',TriangleAlert],['services','Сервисы',Server],['sources','Источники',Radio],['images','Образы',Boxes],['events','Журнал событий',Activity]] as const
export default function App(){
  const [token,setToken]=useState(sessionStorage.getItem('lens-token')||'')
  const [signed,setSigned]=useState(!!token)
  const [page,setPage]=useState('overview')
  const [selected,setSelected]=useState<string|null>(null)
  const qc=useQueryClient()
  const services=useQuery({queryKey:['services'],queryFn:()=>api<Service[]>('/services'),enabled:signed})
  const system=useQuery({queryKey:['system'],queryFn:()=>api<Record<string,string>>('/system'),enabled:signed})
  const demo=useMutation({mutationFn:()=>api<{detail:string}>('/demo',{method:'POST'}),onSuccess:()=>qc.invalidateQueries()})
  if(!signed)return <div className="login"><div className="login-card"><div className="brand"><Shield/> DefenceLens</div><span className="eyebrow">DEFENCE · SECURITY OPERATIONS</span><h1>Видеть сигналы.<br/>Защищать важное.</h1><p>Логи, образы и понятный порядок реагирования в одном рабочем пространстве.</p><form onSubmit={async e=>{e.preventDefault();sessionStorage.setItem('lens-token',token);setSigned(true)}}><label>API-токен<input autoFocus type="password" required value={token} onChange={e=>setToken(e.target.value)} placeholder="Токен из .env"/></label><button className="primary">Открыть рабочее пространство <ArrowUpRight size={16}/></button></form><small>Локальный запуск: токен задаётся в .env. Данные не отправляются внешней LLM.</small></div></div>
  return <div className="app-shell"><aside className="sidebar"><div className="brand"><Shield size={25}/> DefenceLens<span className="brand-dot"/></div><div className="workspace"><span className="workspace-icon">VC</span><div>Операционный центр<small>Defence workspace</small></div><ChevronRight size={14}/></div><span className="nav-label">РАБОЧЕЕ ПРОСТРАНСТВО</span><nav>{nav.map(([id,label,Icon])=><button key={id} className={page===id?'active':''} onClick={()=>{setPage(id);setSelected(null)}}><Icon size={18}/>{label}</button>)}</nav><div className="sidebar-bottom"><div className="local"><span className="dot"/> Локальный анализ<small>Без внешней LLM</small></div><button className="operator" onClick={()=>{sessionStorage.removeItem('lens-token');qc.clear();setSigned(false);setToken('')}}><span className="avatar">OP</span><span>Оператор<small>Завершить сессию</small></span><LogOut size={16}/></button></div></aside>
  <div className="main-shell"><header className="topbar"><span>Workspace <ChevronRight size={14}/> <b>{nav.find(n=>n[0]===page)?.[1]}</b></span><span className="top-status"><span className={'dot '+(system.isError?'bad':'')}/>{system.isError?'Нет связи с API':'Обновление каждые 5 сек'}</span></header><main>
  <div className="page-title"><div><span className="eyebrow">DEFENCE INTELLIGENCE / MVP</span><h1>{nav.find(n=>n[0]===page)?.[1]}</h1><p>{page==='overview'?'Операционная картина. От сигнала к осмысленному действию.':'Доказательства и контекст для уверенных решений.'}</p></div><button className="secondary" disabled={demo.isPending} onClick={()=>demo.mutate()}><FlaskConical size={16}/>{demo.isPending?'Загрузка…':'Загрузить демо'}</button></div>
  <ErrorBox error={services.error||system.error||demo.error}/>{demo.data&&<div className="notice">{demo.data.detail}</div>}
  {page==='overview'&&<Overview open={id=>{setPage('incidents');setSelected(id)}} system={system.data} services={services.data||[]}/>}
  {page==='incidents'&&(selected?<IncidentDetail id={selected} back={()=>setSelected(null)} services={services.data||[]}/>:<Incidents open={setSelected} services={services.data||[]}/>)}
  {page==='services'&&<Services services={services.data||[]}/>}
  {page==='sources'&&<Sources services={services.data||[]}/>}
  {page==='images'&&<Images services={services.data||[]}/>}
  {page==='events'&&<Events services={services.data||[]}/>}
  <footer><Shield size={13}/> DefenceLens <span>Наблюдаемость ≠ доказательство отсутствия угроз</span><span>DEFENCE / 01</span></footer>
  </main></div></div>
}

function Overview({open,system,services}:{open:(id:string)=>void;system?:Record<string,string>;services:Service[]}){
 const d=useQuery({queryKey:['dashboard'],queryFn:()=>api<Dashboard>('/dashboard')})
 const incidents=useQuery({queryKey:['incidents'],queryFn:()=>api<Incident[]>('/incidents')})
 const scans=useQuery({queryKey:['scans'],queryFn:()=>api<Scan[]>('/scans')})
 const sources=useQuery({queryKey:['sources'],queryFn:()=>api<Source[]>('/sources')})
 if(d.isPending)return <Loading/>
 if(!d.data)return <ErrorBox error={d.error}/>
 const x=d.data
 return <><ErrorBox error={d.error||incidents.error||sources.error}/>{x.synthetic_events>0&&<div className="demo-strip"><FlaskConical size={15}/> В потоке есть синтетические события демонстрации — {x.synthetic_events} за последний час</div>}
 <div className="metrics">{[{label:'Активные инциденты',value:x.active_incidents,sub:'Ожидают внимания',icon:TriangleAlert},{label:'События за час',value:x.events_hour,sub:x.events_total+' событий сохранено',icon:Activity},{label:'Ошибки сервера',value:x.errors_hour,sub:'Ответы HTTP 5xx за час',icon:Radio},{label:'Сервисы под наблюдением',value:x.services,sub:x.scans_completed+' образов проанализировано',icon:Server}].map(m=><div className="metric" key={m.label}><div>{m.label}<m.icon size={17}/></div><strong>{m.value.toLocaleString('ru-RU')}</strong><small>{m.sub}</small></div>)}</div>
 <div className="overview-grid"><Panel title="Поток событий" extra={<span className="muted">Последние 60 минут</span>}><div className="chart-legend"><span><i className="legend-green"/>Все события</span><span><i className="legend-orange"/>Ошибки 5xx</span></div><div className="chart"><ResponsiveContainer width="100%" height="100%"><AreaChart data={x.series}><defs><linearGradient id="fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#25967f" stopOpacity={.25}/><stop offset="100%" stopColor="#25967f" stopOpacity={0}/></linearGradient></defs><CartesianGrid strokeDasharray="3 5" vertical={false} stroke="#e7edeb"/><XAxis dataKey="time" tickFormatter={v=>new Date(v).toLocaleTimeString('ru-RU',{hour:'2-digit',minute:'2-digit'})} minTickGap={45} tickLine={false} axisLine={false} fontSize={11}/><YAxis allowDecimals={false} width={28} tickLine={false} axisLine={false} fontSize={11}/><Tooltip labelFormatter={v=>date(String(v))}/><Area isAnimationActive={false} type="monotone" dataKey="events" name="События" stroke="#208d76" fill="url(#fill)" strokeWidth={2}/><Area isAnimationActive={false} type="monotone" dataKey="errors" name="5xx" stroke="#d78948" fill="transparent" strokeWidth={2}/></AreaChart></ResponsiveContainer></div>{x.events_hour===0&&<p className="chart-empty">События пока не поступили. Подключите источник или загрузите демо.</p>}</Panel>
 <Panel title="Индекс внимания" extra={<span className="muted">0–100</span>}><div className="risk-number"><strong>{x.risk}</strong><span>/ 100</span></div><div className="risk-track"><div style={{width:x.risk+'%'}}/></div><p className="risk-label">{x.risk>=60?'Требуется приоритетная проверка':x.risk>0?'Есть сигналы для проверки':'Нет рассчитанных сигналов'}</p><details><summary>Как рассчитан индекс</summary><p>{x.risk_explanation}</p>{x.contributions.map((c,i)=><div className="contribution" key={i}><span>{c.label}</span><b>+{c.points}</b></div>)}</details><p className="muted risk-warning">{x.limitations}</p></Panel></div>
 <div className="overview-grid"><Panel title="Требуют внимания" extra={<span className="count">{x.active_incidents}</span>}><IncidentList incidents={(incidents.data||[]).filter(i=>['open','investigating'].includes(i.status)).slice(0,5)} open={open} services={services}/></Panel><Panel title="Состояние источников"><div className="systems">{Object.entries(system||{}).map(([k,v])=><div key={k}><span>{k==='database'?'PostgreSQL':k==='worker'?'Trivy worker':'Redis'}</span><Badge value={v}/></div>)}</div>{sources.data?.length?sources.data.map(s=><div className="source-row" key={s.id}><div><b>{s.name}</b><small>{date(s.last_received)}</small></div><Badge value={s.state}/></div>):<Empty>Источники не подключены</Empty>}</Panel></div>
 <Panel title="Последние сканирования образов"><ErrorBox error={scans.error}/>{scans.data?.length?scans.data.slice(0,3).map(s=><div className="source-row" key={s.id}><div><b>{s.filename}</b><small>{s.summary?s.summary.vulnerabilities+" CVE · "+s.summary.components+" компонентов · "+s.summary.secrets+" потенциальных секретов":s.error||"Результат ещё не получен"}</small></div><Badge value={s.status}/></div>):<Empty>Загрузите docker save архив в разделе «Образы»</Empty>}</Panel>
 <div className="principle"><Shield size={21}/><div><b>Решение остаётся за оператором</b><p>Рекомендации не выполняют команды. Уязвимость образа не доказывает взлом, а близость событий по времени — причинную связь.</p></div></div></>
}
function IncidentList({incidents,open,services}:{incidents:Incident[];open:(id:string)=>void;services:Service[]}){
 return incidents.length?<div className="incident-list">{incidents.map(i=><button key={i.id} className="incident-row" onClick={()=>open(i.id)}><Badge value={i.priority}/><div><b>{i.title}</b><small>{services.find(s=>s.id===i.service_id)?.name||i.service_id} · {date(i.created_at)}</small></div><Badge value={i.status}/><ChevronRight size={16}/></button>)}</div>:<Empty>Инцидентов нет. Проверьте покрытие и свежесть источников.</Empty>
}
function Incidents({open,services}:{open:(id:string)=>void;services:Service[]}){
 const q=useQuery({queryKey:['incidents'],queryFn:()=>api<Incident[]>('/incidents')})
 const [filter,setFilter]=useState('all')
 return <Panel title="Инциденты" extra={<select aria-label="Фильтр инцидентов" value={filter} onChange={e=>setFilter(e.target.value)}><option value="all">Все статусы</option><option value="open">Открытые</option><option value="investigating">В работе</option><option value="resolved">Решённые</option><option value="false_positive">Ложные срабатывания</option></select>}><ErrorBox error={q.error}/>{q.isPending?<Loading/>:<IncidentList incidents={(q.data||[]).filter(i=>filter==='all'||i.status===filter)} open={open} services={services}/>}</Panel>
}
