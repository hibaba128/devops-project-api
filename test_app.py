import pytest
import json
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'

def test_get_empty_todos(client):
    response = client.get('/todos')
    assert response.status_code == 200
    assert json.loads(response.data) == []

def test_create_todo(client):
    response = client.post('/todos', 
                          json={'title': 'Test Todo', 'description': 'Test Description'})
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['title'] == 'Test Todo'
    assert 'id' in data

def test_create_todo_without_title(client):
    response = client.post('/todos', json={})
    assert response.status_code == 400

def test_get_todo(client):
    create_response = client.post('/todos', json={'title': 'Test'})
    todo_id = json.loads(create_response.data)['id']
    
    get_response = client.get(f'/todos/{todo_id}')
    assert get_response.status_code == 200

def test_update_todo(client):
    create_response = client.post('/todos', json={'title': 'Test'})
    todo_id = json.loads(create_response.data)['id']
    
    update_response = client.put(f'/todos/{todo_id}', 
                                 json={'title': 'Updated', 'completed': True})
    assert update_response.status_code == 200
    data = json.loads(update_response.data)
    assert data['title'] == 'Updated'
    assert data['completed'] == True

def test_delete_todo(client):
    create_response = client.post('/todos', json={'title': 'Test'})
    todo_id = json.loads(create_response.data)['id']
    
    delete_response = client.delete(f'/todos/{todo_id}')
    assert delete_response.status_code == 200
    
    get_response = client.get(f'/todos/{todo_id}')
    assert get_response.status_code == 404