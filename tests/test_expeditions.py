async def test_create_expedition(chief_client):
    response = await chief_client.post("/expeditions/", json={
        "title": "Test Expedition",
        "description": "Test",
        "capacity": 5,
        "start_at": "2030-01-01T00:00:00"
    })
    assert response.status_code == 200
    assert response.json()["title"] == "Test Expedition"
    assert response.json()["status"] == "draft"


async def test_status_draft_to_ready(chief_client):
    exp = await chief_client.post("/expeditions/", json={
        "title": "Test Expedition",
        "description": "Test",
        "capacity": 5,
        "start_at": "2030-01-01T00:00:00"
    })
    exp_id = exp.json()["id"]
    response = await chief_client.patch(f"/expeditions/{exp_id}/status?new_status=ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"


async def test_status_transition_invalid(chief_client):
    exp = await chief_client.post("/expeditions/", json={
        "title": "Test Expedition",
        "description": "Test",
        "capacity": 5,
        "start_at": "2030-01-01T00:00:00"
    })
    exp_id = exp.json()["id"]
    response = await chief_client.patch(f"/expeditions/{exp_id}/status?new_status=active")
    assert response.status_code == 400


async def test_status_ready_to_active_not_enough_members(chief_client):
    exp = await chief_client.post("/expeditions/", json={
        "title": "Test",
        "description": "Test",
        "capacity": 2,
        "start_at": "2020-01-01T00:00:00"
    })
    exp_id = exp.json()["id"]
    await chief_client.patch(f"/expeditions/{exp_id}/status?new_status=ready")
    response = await chief_client.patch(f"/expeditions/{exp_id}/status?new_status=active")
    assert response.status_code == 400


async def test_status_ready_to_active_success(chief_client):
    exp = await chief_client.post("/expeditions/", json={
        "title": "Test",
        "description": "Test",
        "capacity": 2,
        "start_at": "2020-01-01T00:00:00"
    })
    exp_id = exp.json()["id"]

    await chief_client.post("/auth/register", json={"email": "m1@example.com", "name": "Member1", "password": "password", "role": "member"})
    await chief_client.post("/auth/register", json={"email": "m2@example.com", "name": "Member2", "password": "password", "role": "member"})

    await chief_client.post(f"/expeditions/{exp_id}/members", json={"user_email": "m1@example.com"})
    await chief_client.post(f"/expeditions/{exp_id}/members", json={"user_email": "m2@example.com"})
    await chief_client.patch(f"/expeditions/{exp_id}/status?new_status=ready")

    await chief_client.post("/auth/login", json={"email": "m1@example.com", "password": "password"})
    await chief_client.patch(f"/expeditions/{exp_id}/members/confirm")

    await chief_client.post("/auth/login", json={"email": "m2@example.com", "password": "password"})
    await chief_client.patch(f"/expeditions/{exp_id}/members/confirm")

    await chief_client.post("/auth/login", json={"email": "chief@example.com", "password": "password"})
    response = await chief_client.patch(f"/expeditions/{exp_id}/status?new_status=active")

    assert response.status_code == 200
    assert response.json()["status"] == "active"


async def test_member_conflict_active_expeditions(chief_client):
    await chief_client.post("/auth/register", json={"email": "m1@example.com", "name": "Member1", "password": "password", "role": "member"})
    await chief_client.post("/auth/register", json={"email": "m2@example.com", "name": "Member2", "password": "password", "role": "member"})

    exp1 = await chief_client.post("/expeditions/", json={"title": "Exp1", "description": "Test", "capacity": 2, "start_at": "2020-01-01T00:00:00"})
    exp1_id = exp1.json()["id"]

    exp2 = await chief_client.post("/expeditions/", json={"title": "Exp2", "description": "Test", "capacity": 2, "start_at": "2020-01-01T00:00:00"})
    exp2_id = exp2.json()["id"]

    await chief_client.post(f"/expeditions/{exp1_id}/members", json={"user_email": "m1@example.com"})
    await chief_client.post(f"/expeditions/{exp1_id}/members", json={"user_email": "m2@example.com"})
    await chief_client.post(f"/expeditions/{exp2_id}/members", json={"user_email": "m1@example.com"})
    await chief_client.post(f"/expeditions/{exp2_id}/members", json={"user_email": "m2@example.com"})

    await chief_client.post("/auth/login", json={"email": "m1@example.com", "password": "password"})
    await chief_client.patch(f"/expeditions/{exp1_id}/members/confirm")
    await chief_client.patch(f"/expeditions/{exp2_id}/members/confirm")

    await chief_client.post("/auth/login", json={"email": "m2@example.com", "password": "password"})
    await chief_client.patch(f"/expeditions/{exp1_id}/members/confirm")
    await chief_client.patch(f"/expeditions/{exp2_id}/members/confirm")

    await chief_client.post("/auth/login", json={"email": "chief@example.com", "password": "password"})
    await chief_client.patch(f"/expeditions/{exp1_id}/status?new_status=ready")
    await chief_client.patch(f"/expeditions/{exp2_id}/status?new_status=ready")

    r1 = await chief_client.patch(f"/expeditions/{exp1_id}/status?new_status=active")
    assert r1.status_code == 200

    r2 = await chief_client.patch(f"/expeditions/{exp2_id}/status?new_status=active")
    assert r2.status_code == 400

