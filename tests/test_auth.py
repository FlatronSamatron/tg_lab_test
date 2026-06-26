async def test_register_user(client):
    user_data = {
        "email": "chief@example.com",
        "name": "Chief",
        "password": "password",
        "role": "chief"
    }

    response = await client.post("/auth/register", json=user_data)
    assert response.status_code == 200
    
    data = response.json()
    
    assert data["email"] == "chief@example.com"
    assert data["role"] == "chief"
    assert "id" in data


async def test_login(client):
    await client.post("/auth/register", json={
        "email": "chief@example.com",
        "name": "Chief",
        "password": "password",
        "role": "chief"
    })

    response = await client.post("/auth/login", json={
        "email": "chief@example.com",
        "password": "password"
    })

    assert response.status_code == 200
    assert "acces_token" in response.json()
    assert "acces_token" in response.cookies


async def test_register_duplicate_email(client):
    user_data = {
        "email": "chief@example.com",
        "name": "Chief",
        "password": "password",
        "role": "chief"
    }
    await client.post("/auth/register", json=user_data)
    response = await client.post("/auth/register", json=user_data)
    assert response.status_code == 400

    
async def test_login_wrong_password(client):
    await client.post("/auth/register", json={
        "email": "chief@example.com",
        "name": "Chief",
        "password": "password",
        "role": "chief"
    })
    response = await client.post("/auth/login", json={
        "email": "chief@example.com",
        "password": "wrongpass"
    })
    assert response.status_code == 401