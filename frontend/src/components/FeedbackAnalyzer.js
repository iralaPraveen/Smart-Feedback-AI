import React, { useState } from 'react';
import axios from 'axios';
import { Tab, Tabs, TabList, TabPanel } from 'react-tabs';
import { 
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, 
  CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts';
import { 
  FaChartBar, FaSearch, FaSpinner, FaCheckCircle, 
  FaExclamationTriangle, FaFileAlt, FaBrain, FaChartPie 
} from 'react-icons/fa';
import '../styles/FeedbackAnalyzer.css';
import 'react-tabs/style/react-tabs.css';

const FeedbackAnalyzer = () => {
  const [formData, setFormData] = useState({
    spreadsheetId: '',
    rangeName: 'Sheet1!A:B'
  });
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');

  // Colors for charts
  const COLORS = ['#4CAF50', '#F44336', '#FFC107', '#2196F3', '#9C27B0'];

  const handleInputChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const extractSheetId = (url) => {
    const match = url.match(/\/spreadsheets\/d\/([a-zA-Z0-9-_]+)/);
    return match ? match[1] : url;
  };

  const analyzeData = async () => {
    if (!formData.spreadsheetId.trim()) {
      setError('Please enter a Google Sheets ID or URL');
      return;
    }

    setLoading(true);
    setError('');
    setResults(null);

    try {
      const sheetId = extractSheetId(formData.spreadsheetId);
      const response = await axios.post('http://localhost:8000/api/analyze-feedback', {
        spreadsheet_id: sheetId,
        range_name: formData.rangeName
      });

      console.log('📊 Analysis Results:', response.data);
      setResults(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Analysis failed');
      console.error('❌ Analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Transform sentiment data for pie chart
  const getSentimentPieData = () => {
    if (!results?.sentiment_distribution) return [];
    
    return [
      { name: 'Positive', value: results.sentiment_distribution.positive || 0, fill: '#4CAF50' },
      { name: 'Negative', value: results.sentiment_distribution.negative || 0, fill: '#F44336' },
      { name: 'Neutral', value: results.sentiment_distribution.neutral || 0, fill: '#FFC107' }
    ].filter(item => item.value > 0);
  };

  // Transform themes data for bar chart
  const getThemesBarData = () => {
    if (!results?.key_themes) return [];
    
    return Object.entries(results.key_themes).map(([name, count], index) => ({
      name,
      count,
      fill: COLORS[index % COLORS.length]
    }));
  };

  // Format sentiment description for display
  const formatSentimentDescription = (text) => {
    if (!text) return [];
    
    return text.split('\n').map((line, index) => {
      if (line.trim().startsWith('##')) {
        return <h4 key={index} className="section-header">{line.replace('##', '').trim()}</h4>;
      } else if (line.trim().startsWith('-')) {
        return <li key={index} className="bullet-point">{line.trim().substring(1)}</li>;
      } else if (line.trim()) {
        return <p key={index} className="description-text">{line.trim()}</p>;
      }
      return null;
    }).filter(Boolean);
  };

  return (
    <div className="feedback-analyzer">
      {/* Header */}
      <div className="analyzer-header">
        <div className="header-content">
          <div className="header-icon">
            <FaBrain />
          </div>
          <div>
            <h1>🤖 AI Feedback Analyzer</h1>
            <p>Transform Google Forms feedback into actionable insights with AI</p>
          </div>
        </div>
      </div>

      {/* Input Section */}
      <div className="input-section">
        <div className="input-card">
          <h2><FaSearch /> Analyze Your Feedback</h2>
          <div className="form-group">
            <label htmlFor="spreadsheetId">
              Google Sheets URL or ID <span className="required">*</span>
            </label>
            <input
              type="text"
              id="spreadsheetId"
              name="spreadsheetId"
              className="form-input"
              value={formData.spreadsheetId}
              onChange={handleInputChange}
              placeholder="https://docs.google.com/spreadsheets/d/your-sheet-id/edit"
            />
            <small className="help-text">
              💡 Paste the full Google Sheets URL or just the sheet ID
            </small>
          </div>

          <div className="form-group">
            <label htmlFor="rangeName">Data Range (Optional)</label>
            <input
              type="text"
              id="rangeName"
              name="rangeName"
              className="form-input"
              value={formData.rangeName}
              onChange={handleInputChange}
              placeholder="Sheet1!A:B"
            />
          </div>

          <button 
            className={`analyze-button ${loading ? 'loading' : ''}`}
            onClick={analyzeData}
            disabled={loading}
          >
            {loading ? (
              <>
                <FaSpinner className="spinner" />
                Analyzing Feedback...
              </>
            ) : (
              <>
                <FaBrain />
                Analyze with AI
              </>
            )}
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="error-message">
          <FaExclamationTriangle />
          {error}
        </div>
      )}

      {/* Results Section */}
      {results && results.success && (
        <div className="results-section">
          {/* Statistics Overview */}
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon">
                <FaFileAlt />
              </div>
              <div className="stat-content">
                <h3>{results.total_feedback || 0}</h3>
                <p>Total Responses</p>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon success">
                <FaCheckCircle />
              </div>
              <div className="stat-content">
                <h3>{results.statistics?.positive_count || 0}</h3>
                <p>Positive Feedback</p>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">
                <FaChartBar />
              </div>
              <div className="stat-content">
                <h3>{Object.keys(results.key_themes || {}).length}</h3>
                <p>Key Themes</p>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">
                <FaBrain />
              </div>
              <div className="stat-content">
                <h3>{results.suggestions?.length || 0}</h3>
                <p>AI Suggestions</p>
              </div>
            </div>
          </div>

          {/* Tabbed Content */}
          <Tabs className="analysis-tabs">
            <TabList>
              <Tab>📊 Overview</Tab>
              <Tab>🥧 Sentiment Chart</Tab>
              <Tab>📈 Themes Chart</Tab>
              <Tab>💡 Suggestions</Tab>
              <Tab>📝 AI Analysis</Tab>
            </TabList>

            {/* Overview Tab */}
            <TabPanel>
              <div className="analysis-card">
                <h2><FaChartBar /> Analysis Overview</h2>
                <div className="overview-content">
                  <div className="summary-stats">
                    <div className="stat-item">
                      <strong>Total Feedback:</strong> {results.total_feedback}
                    </div>
                    <div className="stat-item">
                      <strong>Analysis Date:</strong> {new Date(results.timestamp).toLocaleString()}
                    </div>
                    <div className="stat-item">
                      <strong>AI Model:</strong> {results.metadata?.ai_model || 'Gemini AI'}
                    </div>
                  </div>

                  {/* Mini Charts Side by Side */}
                  <div className="mini-charts-grid">
                    <div className="mini-chart">
                      <h4>Sentiment Distribution</h4>
                      <ResponsiveContainer width="100%" height={200}>
                        <PieChart>
                          <Pie
                            data={getSentimentPieData()}
                            cx="50%"
                            cy="50%"
                            outerRadius={60}
                            fill="#8884d8"
                            dataKey="value"
                            label={({name, percent}) => `${name}: ${(percent * 100).toFixed(0)}%`}
                          >
                            {getSentimentPieData().map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.fill} />
                            ))}
                          </Pie>
                          <Tooltip />
                        </PieChart>
                      </ResponsiveContainer>
                    </div>

                    <div className="mini-chart">
                      <h4>Top Themes</h4>
                      <ResponsiveContainer width="100%" height={200}>
                        <BarChart data={getThemesBarData().slice(0, 4)}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="name" />
                          <YAxis />
                          <Tooltip />
                          <Bar dataKey="count" fill="#8884d8" />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </div>
              </div>
            </TabPanel>

            {/* Sentiment Chart Tab */}
            <TabPanel>
              <div className="analysis-card">
                <h2><FaChartPie /> Sentiment Distribution</h2>
                <div className="chart-container">
                  <ResponsiveContainer width="100%" height={400}>
                    <PieChart>
                      <Pie
                        data={getSentimentPieData()}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({name, percent, value}) => 
                          `${name}: ${value}% (${(percent * 100).toFixed(1)}%)`
                        }
                        outerRadius={120}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {getSentimentPieData().map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.fill} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>

                {/* Sentiment Description */}
                <div className="sentiment-description">
                  <h3>📝 Sentiment Analysis Description</h3>
                  <div className="description-content">
                    {formatSentimentDescription(results.sentiment_description)}
                  </div>
                </div>
              </div>
            </TabPanel>

            {/* Themes Chart Tab */}
            <TabPanel>
              <div className="analysis-card">
                <h2><FaChartBar /> Key Themes Analysis</h2>
                <div className="chart-container">
                  <ResponsiveContainer width="100%" height={400}>
                    <BarChart
                      data={getThemesBarData()}
                      margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="count" fill="#8884d8" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                <div className="themes-summary">
                  <h3>🎯 Theme Insights</h3>
                  <div className="themes-list">
                    {Object.entries(results.key_themes || {}).map(([theme, count]) => (
                      <div key={theme} className="theme-item">
                        <span className="theme-name">{theme}</span>
                        <span className="theme-count">{count} mentions</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </TabPanel>

            {/* Suggestions Tab */}
            <TabPanel>
              <div className="analysis-card">
                <h2>💡 AI-Generated Suggestions</h2>
                <div className="suggestions-header">
                  <p>Actionable recommendations based on your feedback analysis</p>
                </div>
                <div className="suggestions-grid">
                  {(results.suggestions || []).map((suggestion, index) => (
                    <div key={index} className="suggestion-card">
                      <div className="suggestion-header">
                        <span className="category-badge">AI Generated</span>
                        <span className="priority-badge">💡</span>
                      </div>
                      <p className="suggestion-text">{suggestion}</p>
                    </div>
                  ))}
                </div>
              </div>
            </TabPanel>

            {/* AI Analysis Tab */}
            <TabPanel>
              <div className="analysis-card">
                <h2><FaBrain /> Complete AI Analysis</h2>
                <div className="ai-summary">
                  {results.summary?.split('\n').map((paragraph, index) => {
                    if (paragraph.trim().startsWith('##')) {
                      return <h3 key={index} className="summary-heading">{paragraph.replace('##', '').trim()}</h3>;
                    } else if (paragraph.trim().startsWith('#')) {
                      return <h4 key={index} className="summary-subheading">{paragraph.replace('#', '').trim()}</h4>;
                    } else if (paragraph.trim()) {
                      return <p key={index} className="summary-paragraph">{paragraph.trim()}</p>;
                    }
                    return null;
                  })}
                </div>
              </div>
            </TabPanel>
          </Tabs>
        </div>
      )}
    </div>
  );
};

export default FeedbackAnalyzer;
