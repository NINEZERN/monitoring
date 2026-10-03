export async function api<T>(path:string, options:RequestInit={}):Promise<T>{
  const headers:Record<string,string>={Authorization:'Bearer '+(sessionStorage.getItem('lens-token')||'')};
  if(options.body && !(options.body instanceof FormData)) headers['Content-Type']='application/json';
  const response=await fetch('/api'+path,{...options,headers:{...headers,...options.headers}});
  if(!response.ok){
    const body=await response.json().catch(()=>({detail:'Сервис недоступен'}));
    throw new Error(typeof body.detail==='string'?body.detail:JSON.stringify(body.detail));
  }
  return response.json();
}
export const date=(v:string|null|undefined)=>v?new Date(v).toLocaleString('ru-RU'):'Ещё нет данных';
export const status:Record<string,string>={open:'Открыт',investigating:'В работе',resolved:'Решён',false_positive:'Ложное срабатывание',pending:'Ожидает очереди',queued:'В очереди',running:'Сканируется',retrying:'Повторная попытка',completed:'Готово',failed:'Ошибка',live:'Принимает данные',stale:'Нет свежих данных',never:'Ожидает данных',error:'Ошибка данных',ok:'Доступен',unavailable:'Недоступен',operator_confirmed:'Подтверждено оператором',unverified:'Не подтверждено'};
