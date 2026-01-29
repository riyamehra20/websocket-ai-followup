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
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            message_type = message_data.get("type", "")
            user_text = message_data.get("text", "")
            
            print(f"Received: type={message_type}, text={user_text}, followup_count={followup_count}")
            
            # Handle initial message
            if message_type == "initial":
                followup_count = 1
                
                # Add initial user message to history
                conversation_history.append({"role": "user", "content": user_text})
                
                # Generate first follow-up question
                question = await generate_followup_question(user_text, conversation_history, followup_count)
                
                # Add AI's question to history
                conversation_history.append({"role": "assistant", "content": question})
                
                # Send first follow-up
                response = {
                    "type": "followup",
                    "question": question,
                    "number": followup_count
                }
                await websocket.send_text(json.dumps(response))
                print(f"Sent follow-up #{followup_count}: {question}")
            
            # Handle user answers
            elif message_type == "answer":
                # Add user's answer to history
                conversation_history.append({"role": "user", "content": user_text})
                
                # Check if we need more follow-ups
                if followup_count < 3:
                    followup_count += 1
                    
                    # Generate next follow-up question
                    question = await generate_followup_question(user_text, conversation_history, followup_count)
                    
                    # Add AI's question to history
                    conversation_history.append({"role": "assistant", "content": question})
                    
                    # Send follow-up
                    response = {
                        "type": "followup",
                        "question": question,
                        "number": followup_count
                    }
                    await websocket.send_text(json.dumps(response))
                    print(f"Sent follow-up #{followup_count}: {question}")
                else:
                    # All 3 follow-ups completed
                    final_response = {
                        "type": "complete",
                        "message": "Thanks, we have got your data."
                    }
                    await websocket.send_text(json.dumps(final_response))
                    print("Conversation complete!")
    
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error in WebSocket: {e}")
        import traceback
        traceback.print_exc()
        try:
            await websocket.close()
        except:
            pass