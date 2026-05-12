'use client';

import { useState } from 'react';
import { Send, Settings, Bot, Users } from 'lucide-react';

interface Model {
  id: string;
  name: string;
  enabled: boolean;
}

interface Settings {
  mode: 'standard' | 'detailed' | 'custom';
  arbiterPrompt: string;
  models: Model[];
}

export default function EnsembleAI() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showDetailed, setShowDetailed] = useState(false);
  const [detailedLog, setDetailedLog] = useState<any>(null);

  const [settings, setSettings] = useState<Settings>({
    mode: 'standard',
    arbiterPrompt: 'Ти є Advanced Arbiter. Проаналізуй відповіді worker-моделей і дай найкращу синтезовану відповідь.',
    models: [
      { id: 'qwen2.5:7b-instruct', name: 'Qwen2.5 7B', enabled: true },
      { id: 'llama3.1:8b', name: 'Llama 3.1 8B', enabled: true },
      { id: 'qwen2.5:14b-arbiter', name: 'Qwen2.5 14B Arbiter', enabled: true },
    ]
  });

  const [showSettings, setShowSettings] = useState(false);

  const handleSubmit = async () => {
    if (!query.trim()) return;

    setIsLoading(true);
    setResponse('');
    setDetailedLog(null);

    try {
      const endpoint = settings.mode === 'detailed' 
        ? '/api/v1/ensemble/detailed' 
        : '/api/v1/ensemble';

      const res = await fetch('http://localhost:8000' + endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: query,
          models: settings.models.filter(m => m.enabled).map(m => m.id),
          arbiter_prompt: settings.arbiterPrompt
        })
      });

      const data = await res.json();
      
      if (settings.mode === 'detailed') {
        setDetailedLog(data);
        setResponse(data.final_answer || data.answer || 'No response');
      } else {
        setResponse(data.answer || 'No response');
      }
    } catch (error) {
      setResponse('Помилка підключення до бекенду: ' + (error as Error).message);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleModel = (id: string) => {
    setSettings(prev => ({
      ...prev,
      models: prev.models.map(m => 
        m.id === id ? { ...m, enabled: !m.enabled } : m
      )
    }));
  };

  const saveSettings = () => {
    const json = JSON.stringify(settings, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'ensemble-settings.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex h-screen bg-gray-950 text-white">
      {/* Sidebar */}
      <div className="w-80 border-r border-gray-800 flex flex-col">
        <div className="p-4 border-b border-gray-800">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-gradient-to-br from-purple-500 to-blue-500 rounded-xl flex items-center justify-center">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <h1 className="font-semibold text-xl">Ensemble AI</h1>
              <p className="text-xs text-gray-500">v0.3 MVP</p>
            </div>
          </div>
        </div>

        {/* Models Selection */}
        <div className="p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-medium flex items-center gap-2">
              <Users className="w-4 h-4" /> Моделі
            </h3>
            <button 
              onClick={() => setShowSettings(!showSettings)}
              className="text-gray-400 hover:text-white"
            >
              <Settings className="w-4 h-4" />
            </button>
          </div>

          <div className="space-y-2">
            {settings.models.map(model => (
              <div key={model.id} className="flex items-center justify-between bg-gray-900 rounded-lg p-3">
                <div>
                  <div className="font-medium">{model.name}</div>
                  <div className="text-xs text-gray-500">{model.id}</div>
                </div>
                <button
                  onClick={() => toggleModel(model.id)}
                  className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${model.enabled ? 'bg-emerald-500/20 text-emerald-400' : 'bg-gray-800 text-gray-500'}`}
                >
                  {model.enabled ? 'ON' : 'OFF'}
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Mode Selection */}
        <div className="px-4">
          <label className="text-sm text-gray-400 block mb-2">Режим роботи</label>
          <select 
            value={settings.mode}
            onChange={(e) => setSettings(prev => ({...prev, mode: e.target.value as any}))}
            className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-purple-500"
          >
            <option value="standard">Стандартний Ensemble</option>
            <option value="detailed">Detailed + Reasoning</option>
            <option value="custom">Кастомний (Arbiter)</option>
          </select>
        </div>

        {/* Arbiter Prompt */}
        {settings.mode !== 'standard' && (
          <div className="px-4 mt-4">
            <label className="text-sm text-gray-400 block mb-2">Промпт для Arbiter</label>
            <textarea
              value={settings.arbiterPrompt}
              onChange={(e) => setSettings(prev => ({...prev, arbiterPrompt: e.target.value}))}
              className="w-full h-32 bg-gray-900 border border-gray-700 rounded-lg p-3 text-sm resize-y focus:outline-none focus:border-purple-500"
              placeholder="Введіть кастомний промпт для арбітра..."
            />
            <button
              onClick={saveSettings}
              className="mt-2 w-full bg-gray-800 hover:bg-gray-700 text-sm py-2 rounded-lg transition-colors"
            >
              💾 Зберегти налаштування як JSON
            </button>
          </div>
        )}
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        <div className="h-14 border-b border-gray-800 flex items-center px-6 justify-between">
          <div className="font-medium">Новий запит</div>
          <div className="text-xs text-gray-500">Backend: http://localhost:8000</div>
        </div>

        <div className="flex-1 p-6 overflow-auto">
          {!response && !isLoading && (
            <div className="h-full flex items-center justify-center text-gray-500">
              Введіть запит нижче та натисніть Send
            </div>
          )}

          {isLoading && (
            <div className="flex items-center justify-center h-full">
              <div className="animate-pulse flex flex-col items-center">
                <div className="w-8 h-8 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mb-4"></div>
                <div>Працюють worker-моделі + Arbiter...</div>
              </div>
            </div>
          )}

          {response && (
            <div className="max-w-3xl mx-auto">
              <div className="bg-gray-900 rounded-2xl p-6 mb-6">
                <div className="font-medium mb-3 text-purple-400">Фінальна відповідь:</div>
                <div className="whitespace-pre-wrap leading-relaxed text-lg">
                  {response}
                </div>
              </div>

              {detailedLog && (
                <div className="bg-gray-900/70 rounded-2xl p-5 text-sm">
                  <div className="font-mono text-xs text-gray-500 mb-4">DETAILED LOG</div>
                  <pre className="overflow-auto max-h-96 text-xs text-gray-400">
                    {JSON.stringify(detailedLog, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-gray-800 bg-gray-950">
          <div className="max-w-3xl mx-auto flex gap-3">
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleSubmit())}
              placeholder="Напишіть ваш запит..."
              className="flex-1 bg-gray-900 border border-gray-700 rounded-2xl px-6 py-4 text-lg resize-y min-h-[60px] focus:outline-none focus:border-purple-500"
            />
            <button
              onClick={handleSubmit}
              disabled={isLoading || !query.trim()}
              className="bg-purple-600 hover:bg-purple-700 disabled:bg-gray-700 w-14 h-14 rounded-2xl flex items-center justify-center transition-all active:scale-95"
            >
              <Send className="w-6 h-6" />
            </button>
          </div>
          <div className="text-center text-xs text-gray-600 mt-3">
            Ensemble AI • Паралельна обробка кількома моделями
          </div>
        </div>
      </div>
    </div>
  );
}
