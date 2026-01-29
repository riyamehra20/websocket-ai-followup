from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import json
import os
from ai_service import generate_followup_question

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (frontend)
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
print(f"DEBUG: Looking for frontend files at: {os.path.abspath(frontend_path)}")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")
else:
    print("ERROR: Frontend directory not found!")

@app.get("/")
async def read_root():
    """Serve the main HTML page"""
    html_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    return {"message": "WebSocket AI Follow-up API", "status": "running"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    followup_count = 0
    conversation_history = []
    
    try:
        while True:
            # 1. Wait for message from JS
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_text = message_data.get("text", "")

            # 2. Logic for follow-up questions
            if followup_count < 3:
                followup_count += 1
                
                # IMPORTANT: Add user text to history BEFORE calling the AI
                conversation_history.append({"role": "user", "content": user_text})
                
                # Call AI service with updated history
                question = await generate_followup_question(user_text, conversation_history, followup_count)
                
                # Add AI's new question to history for the next turn
                conversation_history.append({"role": "assistant", "content": question})

                # 3. Send response back to JS (Must be indented inside the 'if')
                response = {
                    "type": "followup",
                    "question": question,
                    "number": followup_count
                }
                await websocket.send_text(json.dumps(response))
            else:
                # 4. Final completion message (Must be indented with the 'if')
                final_response = {"type": "complete", "message": "Thank you for sharing!"}
                await websocket.send_text(json.dumps(final_response))

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")
        try:
            await websocket.close()
        except:
            pass