import {ReactNode} from 'react'
import {AlertCircle,LoaderCircle} from 'lucide-react'
import {status} from './api'
export function Badge({value}:{value:string}){return <span className={'badge badge-'+value}>{status[value]||value}</span>}
export function Empty({children}:{children:ReactNode}){return <div className="empty">{children}</div>}
export function ErrorBox({error}:{error:unknown}){return error?<div role="alert" className="error"><AlertCircle size={18}/>{error instanceof Error?error.message:String(error)}</div>:null}
export function Loading(){return <div className="empty"><LoaderCircle className="spin" size={22}/> Loading data…</div>}
export function Panel({title,children,extra}:{title:string;children:ReactNode;extra?:ReactNode}){return <section className="panel"><div className="panel-heading"><h2>{title}</h2>{extra}</div>{children}</section>}
