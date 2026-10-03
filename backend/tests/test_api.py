import os
os.environ["DATABASE_URL"] = "sqlite:////tmp/lens-test.db"
os.environ["DATA_DIR"] = "/tmp/lens-test-data"
import io
import json
import tarfile
from datetime import datetime, timezone, timedelta
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import Base, engine

@pytest.fixture()
def client():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with TestClient(app) as c:
        c.headers["Authorization"] = "Bearer local-development-token"
        yield c

def setup(c):
    service = c.post("/api/services", json={"name":"API","importance":5}).json()
    source = c.post("/api/sources", json={"name":"Test","service_id":service["id"]}).json()
    return service["id"], source["id"]

def event(n, **kwargs):
    return dict(event_id=str(n), timestamp=(datetime.now(timezone.utc)-timedelta(seconds=120-n)).isoformat(), **kwargs)

def test_auth(client):
    assert client.get("/api/services", headers={"Authorization":""}).status_code == 401

def test_demo_all_detectors_and_idempotence(client):
    assert client.post("/api/demo").status_code == 200
    incidents = client.get("/api/incidents").json()
    assert {x["detector"] for x in incidents} == {"failed_logins","success_after_failures","suspicious_http","server_errors"}
    count = client.get("/api/dashboard").json()["events_total"]
    client.post("/api/demo")
    assert client.get("/api/dashboard").json()["events_total"] == count
    incident = client.get("/api/incidents/"+incidents[0]["id"]).json()
    assert incident["evidence"] and incident["limitations"] and incident["impact"]
    assert all(e["data"]["synthetic"] for e in incident["evidence"])

def test_replay_partial_bad_and_nginx(client):
    sid, src = setup(client)
    logs = [event(1,status=200,path="/"),event(2,status=503,path="/"),{"status":500}]
    a = client.post("/api/ingest/"+src,json=logs).json()
    assert (a["accepted"],a["rejected"]) == (2,1)
    b = client.post("/api/ingest/"+src,json=logs[:2]).json()
    assert (b["accepted"],b["duplicates"]) == (0,2)
    line='127.0.0.1 - - [03/Oct/2025:12:00:00 +0200] "GET / HTTP/1.1" 200 10 "-" "test"'
    r = client.post("/api/sources/"+src+"/upload",files={"file":("access.log",line)})
    assert r.json()["accepted"] == 1
    wrapped = client.post("/api/ingest/"+src,json={"message":line})
    assert wrapped.json()["duplicates"] == 1

def test_late_success(client):
    sid, src = setup(client)
    logs = [event(n,event="login_failed",ip="1.2.3.4",user="a") for n in range(5)]
    client.post("/api/ingest/"+src,json=[event(6,event="login_success",ip="1.2.3.4",user="a")])
    client.post("/api/ingest/"+src,json=logs)
    assert "success_after_failures" in {i["detector"] for i in client.get("/api/incidents").json()}

def test_dependencies_cycle(client):
    db = client.post("/api/services",json={"name":"DB"}).json()
    api = client.post("/api/services",json={"name":"API","dependencies":[db["id"]]}).json()
    assert client.put("/api/services/"+db["id"],json={"name":"DB","dependencies":[api["id"]]}).status_code==422

def test_operator_action_and_no_data_verification(client):
    client.post("/api/demo")
    incident=next(i for i in client.get("/api/incidents").json() if i["detector"]=="server_errors")
    url="/api/incidents/"+incident["id"]
    assert client.post(url+"/actions",json={"status":"investigating","note":"Checked database"}).status_code==200
    assert client.post(url+"/verify").json()["result"]=="insufficient"
    assert len(client.get(url).json()["actions"])==2

def test_archive_rejects_bad_and_traversal(client):
    assert client.post("/api/scans",files={"file":("bad.tar",b"bad")}).status_code==422
    stream=io.BytesIO()
    with tarfile.open(fileobj=stream,mode="w") as t:
        info=tarfile.TarInfo("../escape"); info.size=1
        t.addfile(info,io.BytesIO(b"x"))
    assert client.post("/api/scans",files={"file":("evil.tar",stream.getvalue())}).status_code==422

def test_archive_pending_and_deployment_validation(client):
    sid,src=setup(client)
    stream=io.BytesIO()
    with tarfile.open(fileobj=stream,mode="w") as t:
        for name,content in {"config.json":b"{}", "manifest.json":json.dumps([{"Config":"config.json","Layers":[]}]).encode()}.items():
            info=tarfile.TarInfo(name);info.size=len(content);t.addfile(info,io.BytesIO(content))
    s=client.post("/api/scans",files={"file":("fixture.tar",stream.getvalue())}).json()
    assert s["status"]=="pending"
    d={"service_id":sid,"scan_id":s["id"],"started_at":datetime.now(timezone.utc).isoformat(),"confirmation":"operator_confirmed"}
    assert client.post("/api/deployments",json=d).status_code==422
    d["evidence"]="CI deployment digest verified"
    assert client.post("/api/deployments",json=d).status_code==200

def test_other_principal_cannot_trigger_success(client):
    sid,src=setup(client)
    logs=[event(n,event="login_failed",ip="1.2.3.4",user="a") for n in range(5)]
    logs.append(event(6,event="login_success",ip="1.2.3.4",user="b"))
    client.post("/api/ingest/"+src,json=logs)
    assert "success_after_failures" not in {i["detector"] for i in client.get("/api/incidents").json()}

def test_future_event_rejected(client):
    sid,src=setup(client)
    r=client.post("/api/ingest/"+src,json={"timestamp":(datetime.now(timezone.utc)+timedelta(days=1)).isoformat()})
    assert r.json()["rejected"]==1
