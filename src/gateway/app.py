# app.py
from fastapi import FastAPI, HTTPException, Depends
import requests
from src.schemas.schemas import User, LinkData, Notification
from src.database.database import insert_user, select_links, select_user, insert_link

app = FastAPI()

@app.post("/users/")
async def add_user(user: User):
    try:
        await insert_user(user)
        return {"status": "User added"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await select_user(user_id)
    if user:
        return {"user": dict(user)}
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/links/")
async def add_link(link_data: LinkData):
    try:
        await insert_link(link_data)
        return {"status": "Link added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/links/")
async def delete_link(link_data: LinkData):
    try:
        await delete_link(link_data) 
        return {"status": "Link deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/links/{user_id}")
async def get_links(user_id: int):
    try:
        links = await select_links(user_id)
        return {"links": links}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

        
@app.post("/notify/")
async def notify_user(notification: Notification):
    response = requests.post(f"http://localhost:8001/notify_user", json={"user_id": notification.user_id, "message": notification.message})
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to notify user")
    return {"status": "Notification sent"}