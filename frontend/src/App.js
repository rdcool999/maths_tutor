import React, { useState } from 'react';
import jsPDF from 'jspdf';
import './App.css';

const App = () => {
    const [questions, setQuestions] = useState([]);
    const [loading, setLoading] = useState(false);
    const [config, setConfig] = useState({
        year_level: 3,
        difficulty: 'medium',
        question_type: 'multiple_choice',
        topic: 'arithmetic',
        num_questions: 20
    });

    const generateQuestions = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/generate-math-questions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(config)
            });

            if (!response.ok) {
                throw new Error('Failed to generate questions');
            }

            const data = await response.json();
            setQuestions(data.questions);
        } catch (error) {
            console.error('Error generating questions:', error);
            alert('Failed to generate questions. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleConfigChange = (field, value) => {
        setConfig(prev => ({
            ...prev,
            [field]: field === 'year_level' || field === 'num_questions' ? parseInt(value) : value
        }));
    };

    const getYearDescription = (year) => {
        const descriptions = {
            1: "Basic counting and simple addition",
            2: "Addition, subtraction, and basic multiplication",
            3: "Multiplication tables and division",
            4: "Larger numbers and decimals",
            5: "Fractions, percentages, and coordinates",
            6: "Algebra basics and advanced topics"
        };
        return descriptions[year] || "";
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
            <div className="container mx-auto px-4 py-8">
                {/* Header */}
                <div className="text-center mb-8">
                    <h1 className="text-4xl font-bold text-gray-800 mb-2">🧮 AI Math Question Generator</h1>
                    <p className="text-gray-600 text-lg">Generate unlimited math questions for Year 1-6 students</p>
                </div>

                {/* Configuration Panel */}
                <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
                    <h2 className="text-2xl font-semibold text-gray-800 mb-6">Configure Your Questions</h2>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {/* Year Level */}
                        <div className="space-y-2">
                            <label className="block text-sm font-medium text-gray-700">Year Level</label>
                            <select 
                                value={config.year_level}
                                onChange={(e) => handleConfigChange('year_level', e.target.value)}
                                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            >
                                {[1,2,3,4,5,6].map(year => (
                                    <option key={year} value={year}>Year {year} (Ages {year + 4}-{year + 5})</option>
                                ))}
                            </select>
                            <p className="text-xs text-gray-500">{getYearDescription(config.year_level)}</p>
                        </div>

                        {/* Difficulty */}
                        <div className="space-y-2">
                            <label className="block text-sm font-medium text-gray-700">Difficulty Level</label>
                            <select 
                                value={config.difficulty}
                                onChange={(e) => handleConfigChange('difficulty', e.target.value)}
                                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            >
                                <option value="easy">🟢 Easy</option>
                                <option value="medium">🟡 Medium</option>
                                <option value="hard">🔴 Hard</option>
                            </select>
                        </div>

                        {/* Question Type */}
                        <div className="space-y-2">
                            <label className="block text-sm font-medium text-gray-700">Question Type</label>
                            <select 
                                value={config.question_type}
                                onChange={(e) => handleConfigChange('question_type', e.target.value)}
                                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            >
                                <option value="multiple_choice">📝 Multiple Choice</option>
                                <option value="numerical">🔢 Numerical Answer</option>
                                <option value="comparison">⚖️ Quantitative Comparison</option>
                                <option value="problem_solving">🧩 Problem Solving</option>
                            </select>
                        </div>

                        {/* Topic */}
                        <div className="space-y-2">
                            <label className="block text-sm font-medium text-gray-700">Math Topic</label>
                            <select 
                                value={config.topic}
                                onChange={(e) => handleConfigChange('topic', e.target.value)}
                                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            >
                                <option value="arithmetic">➕ Arithmetic</option>
                                <option value="algebra">📊 Algebra</option>
                                <option value="geometry">📐 Geometry</option>
                            </select>
                        </div>

                        {/* Number of Questions */}
                        <div className="space-y-2">
                            <label className="block text-sm font-medium text-gray-700">Number of Questions</label>
                            <select 
                                value={config.num_questions}
                                onChange={(e) => handleConfigChange('num_questions', e.target.value)}
                                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            >
                                <option value="5">5 Questions</option>
                                <option value="10">10 Questions</option>
                                <option value="20">20 Questions</option>
                            </select>
                        </div>

                        {/* Generate Button */}
                        <div className="space-y-2">
                            <label className="block text-sm font-medium text-gray-700">&nbsp;</label>
                            <button 
                                onClick={generateQuestions}
                                disabled={loading}
                                className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold py-3 px-6 rounded-lg hover:from-blue-600 hover:to-purple-700 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {loading ? (
                                    <span className="flex items-center justify-center">
                                        <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                        </svg>
                                        Generating...
                                    </span>
                                ) : (
                                    '✨ Generate Questions'
                                )}
                            </button>
                        </div>
                    </div>
                </div>

                {/* Questions Display */}
                {questions.length > 0 && (
                    <div className="space-y-6">
                        <div className="text-center">
                            <h2 className="text-2xl font-semibold text-gray-800 mb-2">
                                📚 Your Math Questions ({questions.length} questions)
                            </h2>
                            <p className="text-gray-600">Year {config.year_level} • {config.difficulty} difficulty • {config.topic}</p>
                        </div>
                        
                        <div className="grid gap-6">
                            {questions.map((question, index) => (
                                <QuestionCard key={index} question={question} index={index + 1} />
                            ))}
                        </div>
                    </div>
                )}

                {questions.length === 0 && !loading && (
                    <div className="text-center py-12">
                        <div className="text-6xl mb-4">🎯</div>
                        <h3 className="text-xl font-semibold text-gray-700 mb-2">Ready to Generate Questions!</h3>
                        <p className="text-gray-500">Configure your preferences above and click "Generate Questions" to start.</p>
                    </div>
                )}
            </div>
        </div>
    );
};

const QuestionCard = ({ question, index }) => {
    const [showAnswer, setShowAnswer] = useState(false);

    return (
        <div className="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden">
            <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white p-4">
                <h3 className="text-lg font-semibold">Question {index}</h3>
            </div>
            
            <div className="p-6">
                <p className="text-lg text-gray-800 mb-4 leading-relaxed">{question.question}</p>
                
                {question.options && (
                    <div className="space-y-2 mb-4">
                        {question.options.map((option, idx) => (
                            <div key={idx} className="p-3 bg-gray-50 rounded-lg border border-gray-200 hover:bg-gray-100 transition duration-150">
                                {option}
                            </div>
                        ))}
                    </div>
                )}
                
                <button 
                    onClick={() => setShowAnswer(!showAnswer)}
                    className="bg-green-500 hover:bg-green-600 text-white font-medium py-2 px-4 rounded-lg transition duration-200"
                >
                    {showAnswer ? '🙈 Hide Answer' : '👁️ Show Answer'}
                </button>
                
                {showAnswer && (
                    <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                        <div className="flex items-start space-x-2">
                            <span className="text-green-600 font-semibold">✅ Answer:</span>
                            <span className="text-green-800 font-medium">{question.correct_answer}</span>
                        </div>
                        {question.explanation && (
                            <div className="mt-2 flex items-start space-x-2">
                                <span className="text-green-600 font-semibold">💡 Explanation:</span>
                                <span className="text-green-700">{question.explanation}</span>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default App;