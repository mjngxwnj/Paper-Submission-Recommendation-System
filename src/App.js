import React from 'react';
import { Routes, Route } from 'react-router-dom';
import SearchPage from './components/SearchPage';
import SubmissionPage from './components/SubmissionPage';
import './App.css';

function App() {
  return (
    <Routes>
      <Route path="/" element={<SearchPage />} />
      <Route path="/submission" element={<SubmissionPage />} />
    </Routes>
  );
}

export default App;