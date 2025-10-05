import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    // Check if this is the specific Pydantic validation error
    const errorMessage = error.message || '';
    if (errorMessage.includes('Objects are not valid as a React child') && 
        errorMessage.includes('type, loc, msg, input, ctx')) {
      console.error('Pydantic validation error detected:', error);
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-4 bg-red-50 border border-red-200 rounded-md">
          <h3 className="text-red-800 font-semibold">Something went wrong</h3>
          <p className="text-red-600 mt-2">
            There was an error with form validation. Please refresh the page and try again.
          </p>
          <button 
            onClick={() => this.setState({ hasError: false, error: null })}
            className="mt-3 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Try Again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;