import React, { useState } from 'react';
import axios from 'axios';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, 
  ResponsiveContainer 
} from 'recharts';
import '../styles/FeedbackAnalyzer.css';

const FeedbackAnalyzer = () => {
  const [formData, setFormData] = useState({
    spreadsheetId: '',
    rangeName: 'Sheet1!B:B'
  });
  
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('summary'); // Changed default to 'summary'

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      const response = await axios.post(`${API_URL}/api/analyze-feedback`, {
        spreadsheet_id: formData.spreadsheetId,
        range_name: formData.rangeName
      });

      setResults(response.data);
      console.log('✅ Analysis complete:', response.data);
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'Failed to analyze feedback';
      setError(errorMessage);
      console.error('❌ Analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  const prepareThemeChartData = () => {
    if (!results?.key_themes) return [];
    
    return Object.entries(results.key_themes)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
      .map(([theme, count]) => ({
        theme: theme.charAt(0).toUpperCase() + theme.slice(1),
        mentions: count
      }));
  };

  return (
    <div className="feedback-analyzer">
      <div className="container">
        {/* Header */}
        <header className="header">
          <h1>🤖 SMART FEEDBACK AI</h1>
          <p className="subtitle">AI Analysis System</p>
        </header>

        {/* Input Form */}
        <div className="input-section">
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="spreadsheetId">
                📊 Google Sheet ID
                <span className="required">*</span>
              </label>
              <input
                type="text"
                id="spreadsheetId"
                name="spreadsheetId"
                value={formData.spreadsheetId}
                onChange={handleInputChange}
                placeholder="Enter your Google Spreadsheet ID"
                required
                disabled={loading}
              />
              <small className="help-text">
                Find this in your Google Sheet URL: docs.google.com/spreadsheets/d/<strong>[YOUR_SHEET_ID]</strong>/edit
              </small>
            </div>

            <div className="form-group">
              <label htmlFor="rangeName">
                📍 Range (Optional)
              </label>
              <input
                type="text"
                id="rangeName"
                name="rangeName"
                value={formData.rangeName}
                onChange={handleInputChange}
                placeholder="Sheet1!B:B"
                disabled={loading}
              />
              <small className="help-text">
                Default: Sheet1!B:B (Column B only - feedback text)
              </small>
            </div>

            <button 
              type="submit" 
              className="submit-button"
              disabled={loading}
            >
              {loading ? (
                <>
                  <span className="spinner"></span>
                  Analyzing Feedback...
                </>
              ) : (
                <>
                  <span>🚀</span>
                  Analyze Feedback
                </>
              )}
            </button>
          </form>
        </div>

        {/* Error Message */}
        {error && (
          <div className="error-message">
            <strong>⚠️ Error:</strong> {error}
          </div>
        )}

        {/* Results Section */}
        {results && results.success && (
          <div className="results-section">

            {/* Statistics Cards */}
            <div className="stats-grid">
              <div className="stat-card total">
                <div className="stat-icon">📊</div>
                <div className="stat-content">
                  <div className="stat-value">{results.total_feedback}</div>
                  <div className="stat-label">Total Feedback</div>
                </div>
              </div>

              <div className="stat-card clusters">
                <div className="stat-icon">🔍</div>
                <div className="stat-content">
                  <div className="stat-value">{results.statistics.clusters_found}</div>
                  <div className="stat-label">Clusters Found</div>
                </div>
              </div>

              <div className="stat-card themes">
                <div className="stat-icon">🎯</div>
                <div className="stat-content">
                  <div className="stat-value">{results.statistics.themes_identified}</div>
                  <div className="stat-label">Key Themes</div>
                </div>
              </div>
            </div>

            {/* Tabs Navigation - REORDERED */}
            <div className="tabs">
              <button 
                className={`tab ${activeTab === 'summary' ? 'active' : ''}`}
                onClick={() => setActiveTab('summary')}
              >
                📝 AI Summary
              </button>
              <button 
                className={`tab ${activeTab === 'suggestions' ? 'active' : ''}`}
                onClick={() => setActiveTab('suggestions')}
              >
                💡 Recommendations
              </button>
              <button 
                className={`tab ${activeTab === 'themes' ? 'active' : ''}`}
                onClick={() => setActiveTab('themes')}
              >
                🎯 Themes Analysis
              </button>
              <button 
                className={`tab ${activeTab === 'clusters' ? 'active' : ''}`}
                onClick={() => setActiveTab('clusters')}
              >
                🔍 Cluster Details
              </button>
            </div>

            {/* Tab Content - REORDERED */}
            <div className="tab-content">
              
              {/* Summary Tab - NOW FIRST */}
              {activeTab === 'summary' && (
                <div className="summary-section">
                  <h2>📝 Comprehensive AI Analysis</h2>
                  <div className="summary-content">
                    {results.summary.split('\n').map((paragraph, index) => {
                      if (paragraph.trim().startsWith('##')) {
                        return (
                          <h3 key={index} className="summary-heading">
                            {paragraph.replace(/##/g, '').trim()}
                          </h3>
                        );
                      } else if (paragraph.trim()) {
                        return (
                          <p key={index} className="summary-paragraph">
                            {paragraph.trim()}
                          </p>
                        );
                      }
                      return null;
                    })}
                  </div>
                </div>
              )}

              {/* Suggestions Tab - NOW SECOND */}
              {activeTab === 'suggestions' && (
                <div className="suggestions-section">
                  <h2>💡 AI-Generated Recommendations</h2>
                  <p className="section-description">
                    Specific, actionable recommendations based on customer feedback analysis
                  </p>
                  <div className="suggestions-list">
                    {results.suggestions.map((suggestion, index) => {
                      // Split suggestion into lines
                      const lines = suggestion.split('\n').filter(line => line.trim());
                      const title = lines[0] || suggestion;
                      const description = lines.slice(1).join(' ') || '';
                      
                      return (
                        <div key={index} className="suggestion-item-detailed">
                          <div className="suggestion-header">
                            <span className="suggestion-number">{index + 1}</span>
                            <h3 className="suggestion-title">{title}</h3>
                          </div>
                          {description && (
                            <p className="suggestion-description">{description}</p>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Themes Tab - NOW THIRD */}
              {activeTab === 'themes' && (
                <div className="themes-section">
                  <h2>🎯 Top Themes Identified</h2>
                  <ResponsiveContainer width="100%" height={400}>
                    <BarChart data={prepareThemeChartData()}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="theme" angle={-45} textAnchor="end" height={100} />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="mentions" fill="#667eea" />
                    </BarChart>
                  </ResponsiveContainer>
                  
                  <div className="themes-list">
                    <h3>📋 Theme Details</h3>
                    <div className="theme-items">
                      {Object.entries(results.key_themes)
                        .sort((a, b) => b[1] - a[1])
                        .map(([theme, count]) => (
                          <div key={theme} className="theme-item">
                            <span className="theme-name">{theme.toUpperCase()}</span>
                            <span className="theme-count">{count} mentions</span>
                          </div>
                        ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Clusters Tab - NOW FOURTH */}
              {activeTab === 'clusters' && (
                <div className="clusters-section">
                  <h2>🔍 Feedback Clusters Analysis</h2>
                  <p className="section-description">
                    Feedback automatically grouped into {results.cluster_info.n_clusters} semantic clusters based on similarity.
                  </p>
                  
                  <div className="clusters-grid">
                    {Object.entries(results.cluster_info.cluster_summaries).map(([clusterId, cluster]) => (
                      <div key={clusterId} className="cluster-card">
                        <div className="cluster-header">
                          <h3>Cluster {parseInt(clusterId) + 1}</h3>
                          <span className="cluster-size">{cluster.size} feedbacks</span>
                        </div>
                        <p className="cluster-summary">{cluster.summary}</p>
                        {cluster.sample_feedback && (
                          <div className="cluster-sample">
                            <strong>Sample:</strong> {cluster.sample_feedback.substring(0, 150)}...
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FeedbackAnalyzer;
