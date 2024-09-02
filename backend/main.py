from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from process import process_form
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FormData(BaseModel):
    user_info: str
    form_url: str

@app.get("/")
async def root():
    return {"message": "Welcome to the Form Processing API"}

@app.post('https://shark-033.github.io/web-agent/form')  # Changed to a relative path
async def submit_form(data: FormData):
    user_info = data.user_info
    form_url = data.form_url
    
    if not user_info or not form_url:
        raise HTTPException(status_code=400, detail="Missing user_info or form_url")
    print("processing form")
    # Call the process_form function with user_info and form_url
    process_form(user_info, form_url)  # Pass the JSON data to the function
    return {"message": "Form processed successfully."}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)