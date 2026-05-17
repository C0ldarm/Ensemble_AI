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
  const [abortController, setAbortController] = useState<AbortController | null>(null);

  const [availableModels, setAvailableModels] = useState<string[]>([]);
  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  const [mode, setMode] = useState<'standard' | 'detailed' | 'custom'>('standard');
  
  // Для Detailed режиму
  const [arbiterModel, setArbiterModel] = useState('qwen2.5:14b-arbiter');
  
  // Для Custom режиму
  const [customArbiterModel, setCustomArbiterModel] = useState('qwen2.5:14b-arbiter');
  const [customStrategy, setCustomStrategy] = useState<'majority' | 'argumentation' | 'consensus'>('majority');
  const [customArbiterPrompt, setCustomArbiterPrompt] = useState(
    'You are an Advanced Arbiter. Analyze all responses carefully and give the best final answer.'
  );
  const [allowFollowUp, setAllowFollowUp] = useState(false);

  useEffect(() => {
    axios.get('http://localhost:8000/api/v1/models', { timeout: 0 })
      .then((res) => {
        if (res.data.success) {
          setAvailableModels(res.data.models);
          setSelectedModels([res.data.models[0]]);
          if (res.data.models.includes('qwen2.5:14b-arbiter')) {
            setArbiterModel('qwen2.5:14b-arbiter');
            setCustomArbiterModel('qwen2.5:14b-arbiter');
          }
        }
      });
  }, []);

  const handleModeChange = (newMode: 'standard' | 'detailed' | 'custom') => {
    setMode(newMode);
    // Якщо переходимо від Standard на Detailed/Custom, автоматично додаємо моделі
    if (newMode !== 'standard' && selectedModels.length === 1) {
      const available = availableModels.filter(m => !selectedModels.includes(m));
      const newModels = [selectedModels[0], ...available.slice(0, 2)];
      setSelectedModels(newModels);
    }
    // Якщо переходимо на Standard, залишаємо тільки одну модель
    if (newMode === 'standard' && selectedModels.length > 1) {
      setSelectedModels([selectedModels[0]]);
    }
  };

  const addModel = (model: string) => {
    if (!selectedModels.includes(model)) setSelectedModels([...selectedModels, model]);
  };

  const removeModel = (model: string) => {
    if (mode !== 'standard') {
      setSelectedModels(selectedModels.filter(m => m !== model));
    }
  };

  const cancelRequest = () => {
    if (abortController) {
      abortController.abort();
      setAbortController(null);
      setLoading(false);
      setErrorMsg('Запит скасовано користувачем.');
    }
  };

  const runEnsemble = async () => {
    if (!query.trim() || selectedModels.length === 0) return;

    const controller = new AbortController();
    setAbortController(controller);
    setLoading(true);
    setResponse(null);
    setErrorMsg('');

    try {
      let endpoint = '/api/v1/ensemble';
      const payload: any = {
        prompt: query,
        models: selectedModels,
      };

      if (mode === 'standard') {
        endpoint = '/api/v1/ensemble';
      } else if (mode === 'detailed') {
        endpoint = '/api/v1/ensemble/detailed';
        payload.arbiter_model = arbiterModel;
      } else if (mode === 'custom') {
        endpoint = '/api/v1/ensemble/custom';
        payload.arbiter_model = customArbiterModel;
        payload.strategy = customStrategy;
        payload.arbiter_prompt = customArbiterPrompt;
        payload.allow_follow_up_requests = allowFollowUp;
      }

      const res = await axios.post(`http://localhost:8000${endpoint}`, payload, {
        timeout: 0, // 5 хвилин
        signal: controller.signal,
      });

      setResponse(res.data);
    } catch (err: any) {
      console.error(err);
      if (err.code === 'ECONNABORTED' || err.message === 'canceled') {
        setErrorMsg('Запит скасовано.');
      } else if (err.code === 'ECONNABORTED') {
        setErrorMsg('Таймаут: моделі працюють дуже довго. Спробуйте з меншою кількістю моделей.');
      } else {
        setErrorMsg(err.response?.data?.detail || err.message || 'Network Error');
      }
    } finally {
      setAbortController(null);
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
            ФІНАЛЬНА ВІДПОВІДЬ АРБІТРА ({arbiter.arbiter_model || '—'})
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

        {data.arbiter?.follow_ups?.was_needed && (
          <div className="border border-yellow-200 dark:border-yellow-700 bg-yellow-50 dark:bg-yellow-900/30 rounded-2xl p-5">
            <div className="uppercase text-xs text-yellow-700 dark:text-yellow-400 mb-2">ДОДАТКОВІ ЗАПИТИ (КОНСЕНСУС)</div>
            <div className="text-sm text-yellow-900 dark:text-yellow-300">
              <p className="mb-3">Конфліктні моделі: {data.arbiter.follow_ups.conflicting_models?.join(', ') || 'N/A'}</p>
              {data.arbiter.follow_ups.follow_up_responses && Object.entries(data.arbiter.follow_ups.follow_up_responses).map(([model, response]: any) => (
                <div key={model} className="mb-2">
                  <p className="font-semibold text-xs text-yellow-800 dark:text-yellow-300">{model}:</p>
                  <p className="text-xs text-yellow-800 dark:text-yellow-300 ml-2">{response}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const formatCustom = (data: any) => {
    return formatDetailed(data);
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

            {/* МОДЕЛІ */}
            <div className="mb-6">
              <h3 className="text-xs uppercase text-gray-600 dark:text-gray-500 mb-2">
                МОДЕЛІ ({selectedModels.length})
              </h3>
              
              {mode === 'standard' ? (
                <select
                  value={selectedModels[0] || ''}
                  onChange={(e) => setSelectedModels([e.target.value])}
                  className="w-full bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-xl p-3 text-sm text-gray-900 dark:text-gray-100"
                >
                  <option value="">Виберіть модель</option>
                  {availableModels.map(m => (
                    <option key={m} value={m}>{m}</option>
                  ))}
                </select>
              ) : (
                <>
                  <div className="flex flex-wrap gap-2 mb-3">
                    {selectedModels.map((m) => (
                      <div key={m} className="bg-gray-200 dark:bg-gray-800 px-3 py-1 rounded-xl text-sm flex items-center text-gray-900 dark:text-gray-100">
                        <span className="font-mono text-xs truncate max-w-[170px]">{m}</span>
                        <button onClick={() => removeModel(m)} className="ml-2 text-gray-500 dark:text-gray-400 hover:text-red-600 dark:hover:text-red-400">×</button>
                      </div>
                    ))}
                  </div>
                  <select
                    onChange={(e) => { if (e.target.value) { addModel(e.target.value); e.target.value = ''; }}}
                    className="w-full bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-xl p-3 text-sm text-gray-900 dark:text-gray-100"
                  >
                    <option value="">+ Додати модель</option>
                    {availableModels.filter(m => !selectedModels.includes(m)).map(m => (
                      <option key={m} value={m}>{m}</option>
                    ))}
                  </select>
                </>
              )}
            </div>

            {/* РЕЖИМ */}
            <div className="mb-6">
              <h3 className="text-xs uppercase text-gray-600 dark:text-gray-500 mb-2">РЕЖИМ</h3>
              <select
                value={mode}
                onChange={e => handleModeChange(e.target.value as any)}
                className="w-full bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-xl p-3 text-sm text-gray-900 dark:text-gray-100"
              >
                <option value="standard">Standard</option>
                <option value="detailed">Detailed</option>
                <option value="custom">Custom</option>
              </select>
            </div>

            {/* DETAILED РЕЖИМ */}
            {mode === 'detailed' && (
              <div className="mb-6">
                <h3 className="text-xs uppercase text-gray-600 dark:text-gray-500 mb-2">МОДЕЛЬ АРБІТРА</h3>
                <select
                  value={arbiterModel}
                  onChange={e => setArbiterModel(e.target.value)}
                  className="w-full bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-xl p-3 text-sm text-gray-900 dark:text-gray-100"
                >
                  {availableModels.map(m => (
                    <option key={m} value={m}>{m}</option>
                  ))}
                </select>
              </div>
            )}

            {/* CUSTOM РЕЖИМ */}
            {mode === 'custom' && (
              <>
                <div className="mb-6">
                  <h3 className="text-xs uppercase text-gray-600 dark:text-gray-500 mb-2">МОДЕЛЬ АРБІТРА</h3>
                  <select
                    value={customArbiterModel}
                    onChange={e => setCustomArbiterModel(e.target.value)}
                    className="w-full bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-xl p-3 text-sm text-gray-900 dark:text-gray-100"
                  >
                    {availableModels.map(m => (
                      <option key={m} value={m}>{m}</option>
                    ))}
                  </select>
                </div>

                <div className="mb-6">
                  <h3 className="text-xs uppercase text-gray-600 dark:text-gray-500 mb-2">СТРАТЕГІЯ</h3>
                  <select
                    value={customStrategy}
                    onChange={e => setCustomStrategy(e.target.value as any)}
                    className="w-full bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-xl p-3 text-sm text-gray-900 dark:text-gray-100"
                  >
                    <option value="majority">Вибір більшості</option>
                    <option value="argumentation">Аргументованість</option>
                    <option value="consensus">Консенсус</option>
                  </select>
                </div>

                <div className="mb-6">
                  <label className="flex items-center text-sm text-gray-700 dark:text-gray-300">
                    <input
                      type="checkbox"
                      checked={allowFollowUp}
                      onChange={e => setAllowFollowUp(e.target.checked)}
                      className="mr-2 w-4 h-4"
                    />
                    Дозволити додаткові запити
                  </label>
                </div>

                <div className="mb-6">
                  <h3 className="text-xs uppercase text-gray-600 dark:text-gray-500 mb-2">ПРОМПТ АРБІТРА</h3>
                  <textarea
                    value={customArbiterPrompt}
                    onChange={e => setCustomArbiterPrompt(e.target.value)}
                    className="w-full h-32 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-xl p-3 text-sm text-gray-900 dark:text-gray-100 resize-none"
                    placeholder="Введіть інструкції для арбітра..."
                  />
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
            className="w-full h-52 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-700 rounded-2xl p-5 text-base resize-y text-gray-900 dark:text-gray-100 placeholder-gray-500"
            disabled={loading}
          />

          <div className="flex gap-3 mt-6">
            <button
              onClick={runEnsemble}
              disabled={loading || selectedModels.length === 0}
              className="flex-1 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-400 dark:disabled:bg-gray-700 py-4 rounded-2xl text-lg font-medium transition-all flex items-center justify-center"
            >
              {loading ? (
                <>
                  <span className="animate-spin h-5 w-5 border-2 border-white/30 border-t-white rounded-full mr-2" />
                  Обробка... (до 5 хв)
                </>
              ) : (
                'Запустити Ensemble'
              )}
            </button>

            {loading && (
              <button
                onClick={cancelRequest}
                className="bg-red-600 hover:bg-red-500 text-white py-4 px-6 rounded-2xl font-medium transition-all"
              >
                Стоп
              </button>
            )}
          </div>

          {errorMsg && (
            <div className="mt-4 p-4 bg-red-100 dark:bg-red-900/50 border border-red-300 dark:border-red-700 rounded-2xl text-red-700 dark:text-red-300">
              {errorMsg}
            </div>
          )}

          {response && (
            <div className="mt-10">
              <div className="flex justify-between items-center mb-4">
                <h3 className="font-semibold text-lg text-gray-900 dark:text-white">Результат</h3>
                <button
                  onClick={saveResponseAsJson}
                  className="text-sm bg-gray-300 dark:bg-gray-700 hover:bg-gray-400 dark:hover:bg-gray-600 px-5 py-2 rounded-xl text-gray-900 dark:text-gray-100"
                >
                  Зберегти JSON
                </button>
              </div>

              <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-3xl p-6">
                {mode === 'standard' ? (
                  <p className="text-lg leading-relaxed whitespace-pre-wrap text-gray-900 dark:text-gray-100">
                    {response.final_response || response.final_answer}
                  </p>
                ) : mode === 'custom' ? (
                  formatCustom(response)
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
