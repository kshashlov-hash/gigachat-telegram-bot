import React from 'react';
import "./index.css";

function App() {
  return (
    <div className="app-container">
      {/* ГЛУБОКИЕ ФОНОВЫЕ СФЕРЫ - ДОБАВЛЯЕМ СФЕРУ 3 */}
      <div className="background-glow sphere-1"></div>
      <div className="background-glow sphere-2"></div>
      <div className="background-glow sphere-3"></div>

      <header className="glass-header">
        <nav className="nav-center">
          <span>Главная</span>
          <span>О себе</span>
          <span>Навыки</span>
          <span>Проекты</span>
        </nav>
        <button className="connect-btn">Связаться</button>
      </header>

      <main className="main-content">
        {/* Зона никнейма со стеклянными стрелками - сохраняем */}
        <div className="brand-zone">
          <span className="side-arrow-glass">&lt;</span>

          <div className="logo-glass-box">
            <h1 className="main-logo">MILK</h1>
          </div>

          <span className="side-arrow-glass">&gt;</span>
        </div>

        {/* Остальная часть Bento Grid сохраняется... */}
        <div className="bento-grid">
          <div className="glass-card full-span">
            <h2>Доступна для архитектурных решений</h2>
            <h1>Проектирую надёжный бэкенд и чистые интерфейсы</h1>
            <p>Разрабатываю серверную логику, укрощаю базы данных и собираю всё это в монолитные, работающие как часы проекты.</p>
          </div>

          {/* ...Остальные карточки... */}
          <div className="glass-card portfolio-block">
            <h3>Мои проекты</h3>
            <div className="project-item">
              <span className="project-status live">● Live</span>
              <strong>Gemini AI Telegram Bot</strong>
              <p>Умный ассистент с интеграцией Gemini 1.5 Flash-lite и контекстной памятью.</p>
            </div>
            <div className="project-item">
              <span className="project-status dev">● In Dev</span>
              <strong>Decomposition Monitoring System</strong>
              <p>Система многоуровневого моделирования и мониторинга техногенных объектов на C#.</p>
            </div>
            <div className="tech-icons">
              <span>.py</span> <span>.cs</span> <span>.sql</span>
            </div>
          </div>

          <div className="glass-card stack-block">
            <h3>Опыт & Стек</h3>
            <div className="stack-details">
              <div>
                <h4>// Backend</h4>
                <p>Python (aiogram 3.x)</p>
                <p>C# / C++ (ООП структуры)</p>
                <p>PostgreSQL / SQLite</p>
              </div>
              <div>
                <h4>// Frontend & Tools</h4>
                <p>React + Vite</p>
                <p>Git / GitHub</p>
                <p>Render / Sprinthost</p>
              </div>
            </div>
          </div>

          <div className="glass-card status-block">
            <p>UTF-8 | status = 'coding' <span className="cursor-blink">|</span></p>
            <p className="note">[ Ниже мы расположим остальные блоки в таком же стиле ]</p>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;