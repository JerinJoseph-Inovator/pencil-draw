Set-Location -Path "C:\Users\jerin\Desktop\Pencil_Draw\backend"
& "C:/Users/jerin/Desktop/Pencil_Draw/.venv/Scripts/python.exe" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
