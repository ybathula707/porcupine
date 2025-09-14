'use client';

import { useState, useRef, useEffect } from 'react';

interface TicketData {
  title: string;
  description: string;
  acceptance_criteria: string;
}

interface TicketResponse extends TicketData {
  id: number;
  created_at: string;
  updated_at: string;
}

interface WebSocketMessage {
  type: string;
  message: string;
  timestamp: string;
  progress?: number;
  ticket_id?: number;
  ticket_title?: string;
  error?: string;
}

export default function Home() {
  const [formData, setFormData] = useState<TicketData>({
    title: '',
    description: '',
    acceptance_criteria: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [response, setResponse] = useState<TicketResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [wsMessages, setWsMessages] = useState<WebSocketMessage[]>([]);
  const [wsConnected, setWsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  const connectWebSocket = (ticketId: number) => {
    const baseWsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';
    const wsUrl = `${baseWsUrl}/ws/ticket/${ticketId}/eval`;
    
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.close(); // Close existing connection
    }

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log(`WebSocket connected to ticket ${ticketId}`);
      setWsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        setWsMessages(prev => [...prev, message]);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setWsConnected(false);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setWsConnected(false);
    };
  };

  const disconnectWebSocket = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
      setWsConnected(false);
    }
  };

  // Cleanup WebSocket on component unmount
  useEffect(() => {
    return () => {
      disconnectWebSocket();
    };
  }, []);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  const handleClearForm = () => {
    setFormData({
      title: '',
      description: '',
      acceptance_criteria: ''
    });
    setResponse(null);
    setError(null);
    setWsMessages([]);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    setWsMessages([]); // Clear previous messages

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const res = await fetch(`${apiUrl}/tickets`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data: TicketResponse = await res.json();
      setResponse(data);
      
      // Establish WebSocket connection with the ticket ID after successful creation
      connectWebSocket(data.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200 py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Ticket Content Evaluation
            </h1>
            <p className="text-gray-800">
              Submit a ticket for evaluation with title, description, and acceptance criteria
            </p>
          </div>
        </div>
      </div>

      {/* Split Screen Layout */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 h-full">
          {/* Left Panel - Ticket Form */}
          <div className="bg-white shadow-lg rounded-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Ticket Evaluation Form</h2>
            <form onSubmit={handleSubmit} className="space-y-6">
            {/* Title Field */}
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-900 mb-2">
                Title *
              </label>
              <input
                type="text"
                id="title"
                name="title"
                value={formData.title}
                onChange={handleInputChange}
                required
                className="w-full px-3 py-2 text-gray-900 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="Enter ticket title"
              />
            </div>

            {/* Description Field */}
            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-900 mb-2">
                Description *
              </label>
              <textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                required
                rows={6}
                className="w-full px-3 py-2 text-gray-900 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-vertical"
                placeholder="Enter detailed description of the ticket"
              />
            </div>

            {/* Acceptance Criteria Field */}
            <div>
              <label htmlFor="acceptance_criteria" className="block text-sm font-medium text-gray-900 mb-2">
                Acceptance Criteria *
              </label>
              <textarea
                id="acceptance_criteria"
                name="acceptance_criteria"
                value={formData.acceptance_criteria}
                onChange={handleInputChange}
                required
                rows={6}
                className="w-full px-3 py-2 text-gray-900 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-vertical"
                placeholder="Enter acceptance criteria (e.g., numbered list of requirements)"
              />
            </div>
            {/* Buttons Row */}
            <div className="flex space-x-4">
              {/* Clear Button */}
              <button
                type="button"
                onClick={handleClearForm}
                disabled={isSubmitting}
                className="flex-1 bg-gray-200 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:border-gray-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Clear Form
              </button>
              {/* Submit Button */}
              <button
                type="submit"
                disabled={isSubmitting}
                className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isSubmitting ? 'Evaluating Ticket...' : 'Evaluate Ticket'}
              </button>
            </div>
          </form>

          {/* Error Display */}
          {error && (
            <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-md">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">Error</h3>
                  <p className="text-sm text-red-700 mt-1">{error}</p>
                </div>
              </div>
            </div>
          )}
          </div>

          {/* Right Panel - Real-time Updates */}
          <div className="bg-white shadow-lg rounded-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Real-time Updates</h2>
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${wsConnected ? 'bg-green-500' : 'bg-gray-400'}`}></div>
                <span className="text-sm text-gray-600">
                  {wsConnected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
            </div>
            
            <div className="h-96 overflow-y-auto border border-gray-200 rounded-md p-4 bg-gray-50">
              {wsMessages.length === 0 ? (
                <div className="flex items-center justify-center h-full text-gray-500">
                  <p>Submit a ticket to see real-time evaluation updates</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {wsMessages.map((message, index) => (
                    <div key={index} className="bg-white p-3 rounded-md shadow-sm border-l-4 border-blue-500">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-1">
                            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                              message.type === 'connection' ? 'bg-blue-100 text-blue-800' :
                              message.type === 'ticket_evaluation_start' ? 'bg-yellow-100 text-yellow-800' :
                              message.type === 'ticket_evaluation_progress' ? 'bg-orange-100 text-orange-800' :
                              message.type === 'ticket_evaluation_complete' ? 'bg-green-100 text-green-800' :
                              message.type === 'ticket_evaluation_error' ? 'bg-red-100 text-red-800' :
                              'bg-gray-100 text-gray-800'
                            }`}>
                              {message.type.replace(/_/g, ' ').toUpperCase()}
                            </span>
                          </div>
                          <p className="text-sm text-gray-900 mb-1">{message.message}</p>
                          {message.ticket_id && (
                            <p className="text-xs text-gray-600">Ticket ID: {message.ticket_id}</p>
                          )}
                        </div>
                        <span className="text-xs text-gray-500 ml-2">
                          {new Date(message.timestamp).toLocaleTimeString()}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
