from integration import call
from datetime import datetime, timezone
import uuid
incident=next(i for i in call("/incidents") if i["detector"]=="server_errors")
url="/incidents/"+incident["id"]
call(url+"/actions",{"status":"investigating","note":"Synthetic recovery verification: adding known healthy responses"})
logs=[{"event_id":"recovery-"+uuid.uuid4().hex,"timestamp":datetime.now(timezone.utc).isoformat(),"status":200,"path":"/requests","synthetic":True} for _ in range(12)]
call("/ingest/demo-api",logs)
result=call(url+"/verify",{})
assert result["result"]=="observed_improvement",result
call(url+"/actions",{"status":"open","note":"Демонстрационный инцидент оставлен открытым для просмотра. Проверка восстановления выполнена на явно синтетических событиях."})
print("PASS: verification observes 12 healthy responses after operator action; does not auto-resolve incident")
