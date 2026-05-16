'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { ThemeToggle } from '@/components/ThemeToggle';

export default function EnsembleAI() {
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [errorMsg, setErrorMsg] = useState('');

  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  const [mode, setMode] = useState<'standard' | 'detailed' | 'custom'>('standard');
  const [arbiterPrompt, setArbiterPrompt] = useState(
    'You are an Advanced Arbiter. Analyze all responses carefully and give the best final answer.'
  );
  const [arbiterModel, setArbiterModel] = useState('qwen2.5:14b-arbiter');

  useEffect(() => {
    axios.get('http://localhost:8000/api/v1/models', { timeout: 10000 })
      .then((res) => {
        if (res.data.success) {
          setAvailableModels(res.data.models);
          setSelectedModels(res.data.models.slice(0, 3));
          if (res.data.models.includes('qwen2.5:14b-arbiter')) {
            setArbiterModel('qwen2.5:14b-arbiter');
          }
        }
      });
  }, []);

  const addModel = (model: string) => {
    if (!selectedModels.includes(model)) setSelectedModels([...selectedModels, model]);
  };

  const removeModel = (model: string) => {
    setSelectedModels(selectedModels.filter(m => m !== model));
  };

  const runEnsemble = async () => {
    if (!query.trim() || selectedModels.length === 0) return;

    setLoading(true);
    setResponse(null);
    setErrorMsg('');

    try {
      const endpoint = mode !== 'standard' ? '/api/v1/ensemble/detailed' : '/api/v1/ensemble';

      const payload: any = {
        prompt: query,
        models: selectedModels,
      };

      if (mode !== 'standard') {
        payload.arbiter_prompt = arbiterPrompt;
        payload.arbiter_model = arbiterModel;
      }

      const res = await axios.post(`http://localhost:8000${endpoint}`, payload, {
        timeout: 180000,
      });

      setResponse(res.data);
    } catch (err: any) {
      console.error(err);
      if (err.code === 'ECONNABORTED') {
        setErrorMsg('Таймаут: моделі працюють дуже довго. Спробуйте з меншою кількістю моделей.');
      } else {
        setErrorMsg(err.response?.data?.detail || err.message || 'Network Error');
      }
    } finally {
      setLoading(false);
    }
  };

  const saveResponseAsJson = () => {
    if (!response) return;
    const blob = new Blob([JSON.stringify(response, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `ensemble-response-${Date.now()}.json`;
    a.click();
  };

  const formatDetailed = (data: any) => {
    const arbiter = data.arbiter || {};
    const workers = data.workers || [];

    return (
      <div className="space-y-6">
        <div className="border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 rounded-2xl p-6">
          <div className="uppercase text-xs text-gray-500 dark:text-gray-400 mb-2">
            ФІНАЛЬНА ВІДПОВІДЬ АРБІТРА ({arbiter.model || '—'})
          </div>
          <p className="text-lg leading-relaxed text-gray-900 dark:text-white whitespace-pre-wrap">
            {arbiter.final_answer || arbiter.final_response || "Немає відповіді"}
          </p>
        </div>

        {workers.length > 0 && (
          <div>
            <div className="uppercase text-xs text-gray-500 dark:text-gray-400 mb-3">ВІДПОВІДІ МОДЕЛЕЙ</div>
            <div className="space-y-4">
              {workers.map((w: any, i: number) => (
                <div key={i} className="border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 rounded-2xl p-5">
                  <div className="font-mono text-xs text-blue-600 dark:text-blue-400 mb-2">{w.model}</div>
                  <p className="text-gray-800 dark:text-gray-200 whitespace-pre-wrap">{w.answer || w.response}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {arbiter.reasoning && (
          <div className="border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 rounded-2xl p-5">
            <div className="uppercase text-xs text-gray-500 dark:text-gray-400 mb-2">ПОЯСНЕННЯ АРБІТРА</div>
            <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{arbiter.reasoning}</p>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="flex h-screen bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-100 overflow-hidden">
      {/* Sidebar */}
      <div className={`border-r border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900 transition-all duration-300 ${sidebarOpen ? 'w-72' : 'w-12'} overflow-hidden`}>
        {sidebarOpen ? (
          <div className="p-4 h-full overflow-y-auto">
            <div className="flex items-center justify-between mb-5">
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Ensemble AI</h1>
              <button onClick={() => setSidebarOpen(false)} className="text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white text-xl">←</button>
            </div>

            <div className="mb-6">
              <h3 className="text-xs uppercase text-gray-600 dark:text-gray-500 mb-2">МОДЕЛІ ({selectedModels.length})</h3>
              <div className="flex flex-wrap gap-2 mb-3">
                {selectedModels.map((m) => (
                  <div key={m} className="bg-gray-200 dark:bg-gray-800 px-3 py-1 rounded-xl text-sm flex items-center text-gray-900 dark:text-gray-100">
                    <span className="font-mono text-xs truncate max-w-[170px]">{m}</span>
                    <button onClick={() => removeModel(m)} className="ml-2 text-gray-500 dark:text-gray-400 hover:text-red-600 dark:hover:text-red-400">×</button>
                  </div>
                ))}
              </div>
              <select onChange={(e) => { if (e.target.value) { addModel(e.target.value); e.target.value = ''; }}} 
                      className="w-full bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-xl p-3 text-sm text-gray-900 dark:text-gray-100">
                <option value="">+ Додати модель</option>
                {availableModels.filter(m => !selectedModels.includes(m)).map(m => (
                  <option key={m} value={m}>{m}</option>
                ))}
              </select>
            </div>

            <div className="mb-6">
              <h3 className="text-xs uppercase text-gray-600 dark:text-gray-500 mb-2">РЕЖИМ</h3>
              <select value={mode} onChange={e => setMode(e.target.value as any)} className="w-full bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-xl p-3 text-sm text-gray-900 dark:text-gray-100">
                <option value="standard">Standard</option>
                <option value="detailed">Detailed</option>
                <option value="custom">Custom</option>
              </select>
            </div>

            {(mode === 'detailed' || mode === 'custom') && (
              <>
                <div className="mb-6">
                  <h3 className="text-xs uppercase text-gray-600 dark:text-gray-500 mb-2">МОДЕЛЬ АРБІТРА</h3>
                  <select value={arbiterModel} onChange={e => setArbiterModel(e.target.value)} className="w-full bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-xl p-3 text-sm text-gray-900 dark:text-gray-100">
                    {availableModels.map(m => <option key={m} value={m}>{m}</option>)}
                  </select>
                </div>

                <div className="mb-6">
                  <h3 className="text-xs uppercase text-gray-600 dark:text-gray-500 mb-2">ПРОМПТ АРБІТРА</h3>
                  <textarea value={arbiterPrompt} onChange={e => setArbiterPrompt(e.target.value)} className="w-full h-32 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-2xl p-4 text-sm text-gray-900 dark:text-gray-100 resize-y" />
                </div>
              </>
            )}
          </div>
        ) : (
          <div className="h-full flex items-center justify-center pt-8">
            <button onClick={() => setSidebarOpen(true)} className="text-3xl text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white">→</button>
          </div>
        )}
      </div>

      {/* Main Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="p-5 border-b border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900 flex justify-between items-center">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Запит</h2>
          <ThemeToggle />
        </div>

        <div className="flex-1 p-5 overflow-y-auto">
          <textarea
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="Введіть ваш запит..."
            className="w-full h-52 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-2xl p-5 text-base resize-y text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400"
          />

          <button
            onClick={runEnsemble}
            disabled={loading || selectedModels.length === 0}
            className="w-full mt-6 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-400 dark:disabled:bg-gray-700 py-4 rounded-2xl text-lg font-medium transition-all flex items-center justify-center gap-3 text-white"
          >
            {loading ? (
              <>
                <span className="animate-spin h-5 w-5 border-2 border-white/30 border-t-white rounded-full" />
                Обробка... (до 3 хв)
              </>
            ) : (
              'Запустити Ensemble'
            )}
          </button>

          {errorMsg && (
            <div className="mt-4 p-4 bg-red-100 dark:bg-red-900/50 border border-red-300 dark:border-red-700 rounded-2xl text-red-700 dark:text-red-300">
              {errorMsg}
            </div>
          )}

          {response && (
            <div className="mt-10">
              <div className="flex justify-between items-center mb-4">
                <h3 className="font-semibold text-lg text-gray-900 dark:text-white">Результат</h3>
                <button onClick={saveResponseAsJson} className="text-sm bg-gray-300 dark:bg-gray-700 hover:bg-gray-400 dark:hover:bg-gray-600 px-5 py-2 rounded-xl text-gray-900 dark:text-gray-100 transition-colors">
                  Зберегти JSON
                </button>
              </div>

              <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-3xl p-6">
                {mode === 'standard' ? (
                  <p className="text-lg leading-relaxed whitespace-pre-wrap text-gray-900 dark:text-gray-100">
                    {response.final_response || response.final_answer}
                  </p>
                ) : (
                  formatDetailed(response)
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
