import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import Editor from '@monaco-editor/react'
import { api } from '../api'
import ArrayVisualizer from '../components/ArrayVisualizer'

function Practice() {
  const { levelId } = useParams()
  const [level, setLevel] = useState(null)
  const [code, setCode] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [results, setResults] = useState(null)
  const [running, setRunning] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [aiFeedback, setAiFeedback] = useState(null)
  const [loadingAi, setLoadingAi] = useState(false)

  useEffect(() => {
    fetchLevel()
  }, [levelId])

  const fetchLevel = async () => {
    try {
      const response = await api.getLevel(levelId)
      setLevel(response.data)
      setCode(response.data.starter_code)
    } catch (err) {
      setError('Failed to load level')
    } finally {
      setLoading(false)
    }
  }

  const handleRun = async () => {
    setRunning(true)
    setResults(null)
    setSubmitted(false)
    setAiFeedback(null)
    
    try {
      const response = await api.executeCode(code, levelId)
      setResults(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Execution failed')
    } finally {
      setRunning(false)
    }
  }

  const handleSubmit = async () => {
    if (!results) {
      await handleRun()
      return
    }

    setSubmitting(true)
    
    const failedCases = results.results
      .filter(r => !r.passed)
      .map(r => r.input)
    
    try {
      await api.submitCode(code, levelId, results.passed, failedCases)
      setSubmitted(true)
    } catch (err) {
      setError('Failed to submit')
    } finally {
      setSubmitting(false)
    }
  }

  const handleAskAi = async () => {
    if (!results || results.passed) return;
    
    // Find first failed test case
    const failedCase = results.results.find(r => !r.passed);
    if (!failedCase) return;

    setLoadingAi(true);
    setAiFeedback(null);
    try {
      const resp = await api.getFeedback(
        code, 
        failedCase.actual.startsWith('Error:') ? failedCase.actual : 'Logic Error: Output mismatch',
        failedCase.expected,
        failedCase.actual
      );
      setAiFeedback(resp.data);
    } catch (err) {
      setAiFeedback({
        explanation: 'Failed to connect to AI service.',
        mistake_detection: 'N/A',
        hint: 'Please try again later. Make sure GEMINI_API_KEY is configured.'
      });
    } finally {
      setLoadingAi(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading level...</div>
  }

  if (error && !level) {
    return (
      <div>
        <Link to="/levels" className="back-link">← Back to Levels</Link>
        <div className="error-message">{error}</div>
      </div>
    )
  }

  return (
    <div>
      <Link to="/levels" className="back-link">← Back to Levels</Link>
      
      <div className="flex flex-between mb-32">
        <div>
          <h1 className="page-title">{level.title}</h1>
          <span className={`level-difficulty difficulty-${level.difficulty}`}>
            {level.difficulty}
          </span>
        </div>
        <div className="flex gap-12">
          <button 
            className="btn btn-secondary" 
            onClick={handleRun}
            disabled={running}
          >
            {running ? 'Running...' : 'Run Code'}
          </button>
          <button 
            className="btn btn-primary" 
            onClick={handleSubmit}
            disabled={submitting}
          >
            {submitting ? 'Submitting...' : 'Submit'}
          </button>
        </div>
      </div>

      {submitted && (
        <div className="success-banner">
          <h3>Submission Recorded!</h3>
          <p>Check your dashboard to see your progress.</p>
        </div>
      )}

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="concept-box">
        <h4 className="concept-title">Concept</h4>
        <p className="concept-text">{level.concept}</p>
      </div>

      <div className="card mb-32">
        <h3 className="problem-title">Problem Statement</h3>
        <p className="problem-text">{level.problem}</p>
      </div>

      <div className="editor-container">
        <div className="editor-header">
          <span className="editor-title">Python Code</span>
        </div>
        <Editor
          height="300px"
          defaultLanguage="python"
          theme="vs-dark"
          value={code}
          onChange={(value) => setCode(value || '')}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: 'on',
            scrollBeyondLastLine: false,
            automaticLayout: true,
            tabSize: 4
          }}
        />
      </div>

      <ArrayVisualizer states={results?.results[0]?.states || []} />

      {results && (
        <div className="results-container">
          <h3 className="problem-title">Test Results</h3>
          
          {results.passed ? (
            <div className="success-banner">
              <h3>All Tests Passed!</h3>
              <p>Great job! You can submit your solution.</p>
            </div>
          ) : (
            <div className="mb-20" style={{ color: 'var(--error)', display: 'flex', alignItems: 'center' }}>
              <span>Some tests failed. Check the results below.</span>
              <button 
                className="btn btn-secondary" 
                style={{ marginLeft: '16px' }}
                onClick={handleAskAi}
                disabled={loadingAi}
              >
                {loadingAi ? '🤖 Analyzing...' : '🤖 Ask AI for a Hint'}
              </button>
            </div>
          )}

          {aiFeedback && (
            <div className="card mb-20" style={{ borderColor: 'var(--primary)' }}>
              <h4 style={{ color: 'var(--primary)', marginBottom: '12px', marginTop: 0 }}>🤖 AI Feedback</h4>
              <p><strong>Explanation:</strong> {aiFeedback.explanation}</p>
              <p className="mt-20"><strong>Mistake Detection:</strong> {aiFeedback.mistake_detection}</p>
              <div className="concept-box mt-20" style={{ marginBottom: 0 }}>
                <strong>💡 Hint:</strong> {aiFeedback.hint}
              </div>
            </div>
          )}

          {results.results.map((result, index) => (
            <div 
              key={index} 
              className={`result-item ${result.passed ? 'passed' : 'failed'}`}
            >
              <div className="result-header">
                <span className="result-status">
                  Test Case {index + 1}
                </span>
                <span className={`result-status ${result.passed ? 'status-passed' : 'status-failed'}`}>
                  {result.passed ? '✓ Passed' : '✗ Failed'}
                </span>
              </div>
              <div className="result-details">
                <div>
                  <div className="input-label">Input</div>
                  <div className="result-value">{result.input}</div>
                </div>
                <div>
                  <div className="input-label">Expected</div>
                  <div className="result-value">{result.expected}</div>
                </div>
                <div>
                  <div className="input-label">Actual</div>
                  <div className="result-value" style={{ 
                    color: result.passed ? 'var(--success)' : 'var(--error)' 
                  }}>
                    {result.actual}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default Practice
