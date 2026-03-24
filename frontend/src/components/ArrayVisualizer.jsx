import { useState, useEffect } from 'react';

export default function ArrayVisualizer({ states }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    let timer;
    if (isPlaying && currentIndex < states.length - 1) {
      timer = setTimeout(() => {
        setCurrentIndex(prev => prev + 1);
      }, 800);
    } else if (currentIndex >= states.length - 1) {
      setIsPlaying(false);
    }
    return () => clearTimeout(timer);
  }, [isPlaying, currentIndex, states.length]);

  if (!states || states.length === 0) {
    return (
      <div className="visualizer-empty">
        <p>No visualization states found.</p>
        <p className="text-sm text-gray">Add <code>visualize(arr=..., i=...)</code> in your code to see step-by-step execution.</p>
      </div>
    );
  }

  const currentState = states[currentIndex];
  // Extract main array if present
  let mainArray = currentState.arr || currentState.array || currentState.nums || currentState.data;
  if (!Array.isArray(mainArray)) {
    // try to find first array in the state
    for (const [key, value] of Object.entries(currentState)) {
      if (Array.isArray(value)) {
        mainArray = value;
        break;
      }
    }
  }

  // Extract variables to treat as pointers
  const variables = Object.entries(currentState).filter(([k, v]) => !Array.isArray(v) && k !== 'topic');

  return (
    <div className="visualizer-container">
      <div className="flex flex-between mb-16">
        <h3 className="section-title m-0">Execution Visualizer</h3>
        <div className="flex gap-12 align-center">
          <span className="step-counter">Step {currentIndex + 1} of {states.length}</span>
          <button 
            className="btn btn-sm btn-secondary" 
            onClick={() => setCurrentIndex(0)}
            disabled={currentIndex === 0}
            title="Reset"
          >
            ⏮
          </button>
          <button 
            className="btn btn-sm btn-secondary" 
            onClick={() => setCurrentIndex(prev => Math.max(0, prev - 1))}
            disabled={currentIndex === 0}
            title="Previous Step"
          >
            ◀
          </button>
          <button 
            className={`btn btn-sm ${isPlaying ? 'btn-error' : 'btn-primary'}`} 
            onClick={() => {
              if (currentIndex >= states.length - 1) setCurrentIndex(0);
              setIsPlaying(!isPlaying);
            }}
            title={isPlaying ? "Pause" : "Play"}
          >
            {isPlaying ? '⏸' : '▶'}
          </button>
          <button 
            className="btn btn-sm btn-secondary" 
            onClick={() => setCurrentIndex(prev => Math.min(states.length - 1, prev + 1))}
            disabled={currentIndex >= states.length - 1}
            title="Next Step"
          >
            ▶
          </button>
        </div>
      </div>

      <div className="visualizer-canvas">
        {mainArray ? (
          <div className="array-display">
            {mainArray.map((val, idx) => {
              // Find matching pointers for this index
              const pointersHere = variables.filter(([_, pointVal]) => pointVal === idx);
              return (
                <div key={idx} className="array-item-container">
                  <div className="array-index">{idx}</div>
                  <div className={`array-box ${pointersHere.length > 0 ? 'highlighted' : ''}`}>
                    {val}
                  </div>
                  <div className="pointers-container">
                    {pointersHere.map(([name, _]) => (
                      <div key={name} className="pointer-label">{name} ↑</div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="variables-only">
            {variables.map(([k, v]) => (
              <div key={k} className="var-box">
                <span className="var-name">{k}</span>
                <span className="var-value">{String(v)}</span>
              </div>
            ))}
          </div>
        )}
      </div>
      
      {/* Show all local variables horizontally as well */}
      <div className="variables-bar mt-20">
        <div className="variables-bar-title">Local Variables:</div>
        <div className="flex gap-12">
          {variables.length > 0 ? variables.map(([k, v]) => (
            <div key={k} className="mini-var">
              <code>{k}</code> = <span>{String(v)}</span>
            </div>
          )) : <span className="text-gray">None</span>}
        </div>
      </div>
    </div>
  );
}
