import React, { useState } from 'react';

export default function LeaveModal() {
  const [formData, setFormData] = useState({
    employee_name: '',
    leave_type: 'Sick Leave',
    start_date: '',
    end_date: '',
    medical_reason: ''
  });
  const [isParsing, setIsParsing] = useState(false);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setIsParsing(true);
    const dataPayload = new FormData();
    dataPayload.append('file', file);

    try {
      // POST the binary chunk stream directly to your FastAPI parsing microservice
      const response = await fetch('http://localhost:8000/api/v1/documents/parse-leave-slip', {
        method: 'POST',
        body: dataPayload,
      });

      const parsedResult = await response.json();

      if (!parsedResult.error) {
        // 🔥 MAGIC STEP: Update our form input state completely from the LLM JSON response!
        setFormData({
          employee_name: parsedResult.employee_name || '',
          leave_type: parsedResult.leave_type || 'Sick Leave',
          start_date: parsedResult.start_date || '',
          end_date: parsedResult.end_date || '',
          medical_reason: parsedResult.medical_reason || ''
        });
      } else {
        alert(`Parsing Failed: ${parsedResult.error}`);
      }
    } catch (err) {
      console.error('Error contacting document analysis pipeline:', err);
    } finally {
      setIsParsing(false);
    }
  };

  return (
    <div className="modal-drawer">
      <h3>Submit Leave Request</h3>
      <input type="file" onChange={handleFileUpload} accept=".pdf,.docx" />
      {isParsing && <p className="loading-spinner">🧠 SmartHR AI Copilot is parsing document fields...</p>}
      
      {/* Bind form fields cleanly to state variables */}
      <input type="text" value={formData.employee_name} onChange={(e) => setFormData({...formData, employee_name: e.target.value})} placeholder="Employee Name" />
      <input type="date" value={formData.start_date} onChange={(e) => setFormData({...formData, start_date: e.target.value})} />
      <input type="date" value={formData.end_date} onChange={(e) => setFormData({...formData, end_date: e.target.value})} />
    </div>
  );
}