import React, { useState } from 'react';
import avatarImg from "./Avatar.jpg";
import "./index.css";

function App() {
  const [isAvatarOpen, setIsAvatarOpen] = useState(false);

  return (
    <div className="app-container">
      <div className="ios-bg-sphere-1"></div>
      <div className="ios-bg-sphere-2"></div>

      <main className="main-content">
        {/* iOS Header */}
        <header className="ios-header-zone">
          <div className="profile-container">
            <div
              className="avatar-container"
              onClick={() => setIsAvatarOpen(true)}
              title="Открыть фото"
            >
              <img src={avatarImg} alt="MILK" className="avatar-img" />
            </div>
            <div className="profile-info">
              <span className="subtitle">Bots & Automation Crafter</span>
              <h1 className="main-logo-apple">MILK</h1>
            </div>
          </div>
          <button
            className="ios-connect-btn"
            onClick={() => window.open('https://t.me/milkshakese', '_blank')}
          >
            Связаться
          </button>
        </header>

        {/* Apple Bento Grid */}
        <div className="apple-bento-grid">
          {/* Welcome Widget */}
          <div className="apple-glass-card welcome-widget">
            <div className="widget-header">
              <span className="widget-icon">⚡</span>
              <h3>Обо мне</h3>
            </div>
            <h1>Создаю ботов, интерактивные веб-сайты и AI-интеграции</h1>
            <p>Разрабатываю умных Telegram-ботов, собираю стильные веб-визитки и лендинги, а также подключаю нейросети для автоматизации задач.</p>
          </div>

          {/* Portfolio Widget */}
          <div
            className="apple-glass-card portfolio-widget-ios"
            onClick={() => window.open('https://github.com/kshashlov-hash', '_blank')}
          >
            <div>
              <div className="widget-header-small">
                <span className="widget-icon">📁</span>
                <h3>Проекты</h3>
              </div>
              <p className="project-highlight">AI Assistants, Bots & Web</p>
            </div>
            <p className="action-hint">GitHub ↗</p>
          </div>

          {/* Status Widget */}
          <div className="apple-glass-card status-widget-ios">
            <div className="widget-header-small">
              <span className="widget-icon">💻</span>
              <h3>Статус</h3>
            </div>
            <div className="status-indicator">
              <div className="dot online"></div>
              <span>Building</span>
            </div>
            <p className="monospace-ios">UTF-8 | Python & React</p>
          </div>

          {/* Stack Widget */}
          <div className="apple-glass-card stack-widget">
            <div className="widget-header">
              <span className="widget-icon">🛠</span>
              <h3>Стек & Направления</h3>
            </div>
            <div className="stack-details-ios">
              <div>
                <h4>// Bots & AI</h4>
                <p>Python (aiogram 3.x)</p>
                <p>Интеграция GigaChat / Gemini API</p>
                <p>C# / SQL (Логика и БД)</p>
              </div>
              <div className="separator"></div>
              <div>
                <h4>// Frontend & Tools</h4>
                <p>React + Vite (Лендинги / WebApp)</p>
                <p>Tailwind CSS & Glassmorphic Design</p>
                <p>Git / Docker / Linux</p>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* FULLSCREEN IMAGE MODAL */}
      {isAvatarOpen && (
        <div className="image-modal-overlay" onClick={() => setIsAvatarOpen(false)}>
          <div className="image-modal-content">
            <img src={avatarImg} alt="MILK Full" className="full-avatar-img" />
            <span className="close-modal-hint">Нажми в любом месте, чтобы закрыть</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;