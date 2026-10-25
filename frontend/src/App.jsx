import { useState, useEffect } from 'react';

function App() {
  const [notes, setNotes] = useState([]);
  const [inputText, setInputText] = useState("");

  // 1. Загружаем заметки из Python при открытии страницы
  useEffect(() => {
    fetch('http://localhost:8000/api/notes')
      .then(response => response.json())
      .then(data => setNotes(data.notes))
      .catch(error => console.error("Ошибка загрузки:", error));
  }, []);

  // 2. Функция добавления заметки (теперь с отправкой в Python)
  const handleAddNote = async () => {
    if (inputText.trim() === "") return;

    try {
      const response = await fetch('http://localhost:8000/api/notes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: inputText })
      });
      
      const data = await response.json();
      setNotes(data.notes); // Обновляем список тем, что прислал Python
      setInputText("");     // Очищаем поле
    } catch (error) {
      console.error("Ошибка отправки:", error);
    }
  };
  const handleDeleteNote = async (id) => {
    try {
      const response = await fetch(`http://localhost:8000/api/notes/${id}`, {
        method: 'DELETE',
      });
      const data = await response.json();
      setNotes(data.notes); // Обновляем список после удаления
    } catch (error) {
      console.error("Ошибка удаления:", error);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
      <div className="bg-white p-8 rounded-2xl shadow-2xl w-full max-w-md">
        
        <h1 className="text-2xl font-bold text-gray-800 mb-6 text-center">
          Мои заметки
        </h1>

        <div className="flex gap-2 mb-6">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            className="border border-gray-300 rounded-lg p-2 flex-grow focus:outline-none focus:border-blue-500 text-gray-800"
            placeholder="Напиши что-нибудь..."
          />
          <button
            onClick={handleAddNote}
            className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition"
          >
            Добавить
          </button>
        </div>

       <ul className="space-y-2">
          {notes.map((note) => (
            <li key={note.id} className="bg-gray-100 p-3 rounded-lg text-gray-800 border border-gray-200 flex justify-between items-center">
              <span>{note.text}</span>
              <button 
                onClick={() => handleDeleteNote(note.id)}
                className="text-red-500 hover:text-red-700 font-bold px-2 cursor-pointer"
                title="Удалить"
              >
                ✕
              </button>
            </li>
          ))}
        </ul>

      </div>
    </div>
  );
}

export default App;