from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# --- НАСТРОЙКА БАЗЫ ДАННЫХ ---
# Говорим Python'у создать файл базы данных notes.db в папке с проектом
SQLALCHEMY_DATABASE_URL = "sqlite:///./notes.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- МОДЕЛЬ ДЛЯ БАЗЫ ДАННЫХ ---
# Это описание таблицы, в которой будут храниться заметки
class NoteDB(Base):
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)

# Эта строчка создает саму базу данных и таблицу при запуске
Base.metadata.create_all(bind=engine)

# --- СХЕМЫ ДЛЯ FASTAPI (Pydantic) ---
class NoteCreate(BaseModel):
    text: str

class NoteResponse(BaseModel):
    id: int
    text: str
    class Config:
        from_attributes = True # Разрешаем FastAPI читать данные из SQLAlchemy

# --- САМО ПРИЛОЖЕНИЕ ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"], # Разрешил оба порта на всякий случай
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Функция для подключения к базе данных при каждом запросе
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. Получаем заметки ИЗ БАЗЫ ДАННЫХ
@app.get("/api/notes")
def get_notes(db: Session = Depends(get_db)):
    notes = db.query(NoteDB).all()
    return {"notes": notes}

# 2. Сохраняем заметку В БАЗУ ДАННЫХ
@app.post("/api/notes")
def add_note(note: NoteCreate, db: Session = Depends(get_db)):
    new_note = NoteDB(text=note.text)
    db.add(new_note)
    db.commit()          # Сохраняем изменения
    db.refresh(new_note) # Обновляем данные из базы
    notes = db.query(NoteDB).all()
    return {"notes": notes}
# 3. Удаление заметки по ID
@app.delete("/api/notes/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(NoteDB).filter(NoteDB.id == note_id).first()
    if note:
        db.delete(note)
        db.commit()
    notes = db.query(NoteDB).all()
    return {"notes": notes}
@app.get("/api/hello")
def read_root():
    return {"message": "Привет из Python! Связь работает!"}