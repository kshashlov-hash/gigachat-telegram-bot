import React from 'react';

function App() {
  const navLinks = [
    { title: 'Главная', href: '#home' },
    { title: 'О себе', href: '#about' },
    { title: 'Навыки', href: '#skills' },
    { title: 'Проекты', href: '#projects' },
  ];

  return (
    <div className="min-h-screen bg-[#0b1120] text-slate-100 font-sans antialiased selection:bg-cyan-500/30 selection:text-cyan-200">

      {/* --- НАЧАЛО ШАПКИ (HEADER) --- */}
      <header className="sticky top-0 z-50 w-full border-b border-slate-800/60 bg-[#0b1120]/70 backdrop-blur-xl">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">

       {/* Логотип </milk> в строгом сером стиле с вынесенным ярлыком */}
<div className="relative group cursor-pointer select-none py-2 px-6 flex items-center justify-center isolate">

  {/* Инженерно-абстрактный коллаж на фоне */}
  <div className="absolute inset-0 flex items-center justify-center pointer-events-none">

    {/* Серый матовый круг с аккуратной светлой обводкой */}
    <div className="absolute w-11 h-11 bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700/80 rounded-full -translate-x-6 translate-y-0.5 opacity-95 transition-all duration-300 ease-out group-hover:scale-105 group-hover:border-slate-500" />

    {/* Всплывающий ярлык — теперь при наведении остаётся на месте по Y и выравнивается в rotate-0 */}
    <div className="absolute w-7 h-5 border-2 border-slate-700 bg-slate-800 rounded-md transform -rotate-12 translate-x-14 -translate-y-0 shadow-[0_4px_14px_rgba(0,0,0,0.6)] transition-all duration-300 ease-out group-hover:translate-x-14 group-hover:-translate-y-0 group-hover:rotate-0 group-hover:border-cyan-400 group-hover:bg-slate-700">

      {/* Внутренние полоски шлейфа */}
      <div className="absolute left-1 top-1.5 w-3 h-0.5 bg-cyan-400 rounded-none opacity-90" />
      <div className="absolute left-1 top-3 w-2 h-0.5 bg-cyan-400 rounded-none opacity-90" />
    </div>
  </div>

  {/* Текст логотипа */}
  <div className="relative z-10 flex items-center gap-0.5 font-mono text-xl font-bold tracking-tight text-white drop-shadow-[0_2px_4px_rgba(11,17,32,0.8)]">
    <span className="text-cyan-400 transition-transform group-hover:-translate-x-0.5 inline-block">&lt;/</span>
    <span className="text-white tracking-wide">milk</span>
    <span className="text-cyan-400 transition-transform group-hover:translate-x-0.5 inline-block">&gt;</span>
  </div>
</div>

          {/* Навигация */}
          <nav className="hidden md:flex items-center gap-8">
            {navLinks.map((link) => (
              <a
                key={link.title}
                href={link.href}
                className="text-sm font-medium text-slate-400 hover:text-cyan-400 transition-colors duration-200 relative group py-1"
              >
                {link.title}
                <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-cyan-400 transition-all duration-200 group-hover:w-full" />
              </a>
            ))}
          </nav>

          {/* Кнопка действия */}
          <div className="flex items-center">
            <a
              href="#contacts"
              className="px-4 py-2 text-sm font-medium text-cyan-400 border border-cyan-500/30 rounded-xl bg-cyan-500/5 hover:bg-cyan-500/10 hover:border-cyan-400 hover:shadow-[0_0_15px_rgba(34,211,238,0.15)] transition-all duration-200"
            >
              Связаться
            </a>
          </div>

        </div>
      </header>
      {/* --- КОНЕЦ ШАПКИ --- */}

      {/* --- ГЛАВНЫЙ ЭКРАН (HERO SECTION) --- */}
      <main id="home" className="max-w-6xl mx-auto px-4 pt-12 pb-16">

        {/* Сетка Bento Grid из матовых окошек */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

          {/* Левое большое стекло (Основное приветствие) */}
          <div className="md:col-span-2 relative overflow-hidden rounded-3xl border border-slate-800/80 bg-slate-900/40 p-8 backdrop-blur-xl flex flex-col justify-between min-h-[340px] shadow-2xl">
            {/* Мягкое внутреннее свечение под стеклом */}
            <div className="absolute -top-24 -left-24 w-48 h-48 bg-cyan-500/10 blur-[80px] rounded-full pointer-events-none" />

            <div>
              {/* Аккуратное облачко-статус */}
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium mb-6">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                Доступна для архитектурных решений
              </div>

              <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-white mb-4 leading-tight">
                Проектирую надёжный <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">бэкенд</span> <br />
                и чистые интерфейсы.
              </h1>

              <p className="text-slate-400 max-w-xl text-base sm:text-lg font-normal leading-relaxed">
                Разрабатываю серверную логику, укрощаю базы данных и собираю всё это в монолитные, работающие как часы проекты.
              </p>
            </div>

            {/* Группа кнопок-блоков */}
            <div className="flex flex-wrap gap-4 mt-8">
              <a href="#projects" className="px-5 py-3 bg-cyan-500 text-slate-950 font-semibold rounded-xl hover:bg-cyan-400 transition-all duration-200 shadow-lg shadow-cyan-500/20">
                Мои проекты
              </a>
              <a href="#about" className="px-5 py-3 bg-slate-800/60 border border-slate-700/50 text-slate-300 font-medium rounded-xl hover:bg-slate-700/60 transition-all duration-200">
                Опыт & Стек
              </a>
            </div>
          </div>

          {/* Правое окошко (Имитация IDE / Стек технологий) */}
          <div className="rounded-3xl border border-slate-800/80 bg-slate-900/30 p-6 backdrop-blur-xl flex flex-col justify-between shadow-2xl relative overflow-hidden">
            <div className="absolute -bottom-24 -right-24 w-48 h-48 bg-blue-500/10 blur-[80px] rounded-full pointer-events-none" />

            <div>
              {/* Шапка "окна" с кнопками управления */}
              <div className="flex items-center gap-1.5 border-b border-slate-800/80 pb-4 mb-4">
                <div className="w-2.5 h-2.5 rounded-full bg-slate-700" />
                <div className="w-2.5 h-2.5 rounded-full bg-slate-700" />
                <div className="w-2.5 h-2.5 rounded-full bg-slate-700" />
                <span className="text-xs font-mono text-slate-500 ml-2">stack.json</span>
              </div>

              {/* Теги внутри окошка */}
              <div className="space-y-4">
                <div>
                  <span className="text-xs font-mono text-slate-500 block mb-2">// Основной инструментарий</span>
                  <div className="flex flex-wrap gap-2">
                    <span className="px-2.5 py-1 text-xs font-mono rounded-lg bg-slate-800 border border-slate-700/80 text-cyan-400">Python</span>
                    <span className="px-2.5 py-1 text-xs font-mono rounded-lg bg-slate-800 border border-slate-700/80 text-cyan-400">C#</span>
                    <span className="px-2.5 py-1 text-xs font-mono rounded-lg bg-slate-800 border border-slate-700/80 text-cyan-400">SQL</span>
                  </div>
                </div>

                <div>
                  <span className="text-xs font-mono text-slate-500 block mb-2">// Фронтенд & Окружение</span>
                  <div className="flex flex-wrap gap-2">
                    <span className="px-2.5 py-1 text-xs font-mono rounded-lg bg-slate-800/40 border border-slate-800 text-slate-400">React</span>
                    <span className="px-2.5 py-1 text-xs font-mono rounded-lg bg-slate-800/40 border border-slate-800 text-slate-400">Tailwind</span>
                    <span className="px-2.5 py-1 text-xs font-mono rounded-lg bg-slate-800/40 border border-slate-800 text-slate-400">Vite</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Подвал окошка */}
            <div className="pt-4 border-t border-slate-800/60 mt-6 text-xs font-mono text-slate-500 flex justify-between items-center">
              <span>UTF-8</span>
              <span className="text-cyan-500/60">status = "coding"</span>
            </div>
          </div>

        </div>

        {/* Заглушка для демонстрации скролла */}
        <div className="h-[400px] mt-12 text-slate-700 text-xs font-mono flex items-center justify-center border border-dashed border-slate-800/60 rounded-3xl">
          [ Ниже мы расположим остальные блоки в таком же стиле ]
        </div>
      </main>

    </div>
  );
}

export default App;