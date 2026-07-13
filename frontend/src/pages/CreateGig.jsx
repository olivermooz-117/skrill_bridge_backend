import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import './CreateGig.css';

const CreateGig = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    price: '',
    delivery_days: '',
    tags: [],
  });
  const [tagInput, setTagInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [debugInfo, setDebugInfo] = useState('');

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setError('');
  };

  const handleAddTag = (e) => {
    e.preventDefault();
    if (tagInput.trim() && !formData.tags.includes(tagInput.trim())) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, tagInput.trim()]
      }));
      setTagInput('');
    }
  };

  const handleRemoveTag = (tagToRemove) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }));
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAddTag(e);
    }
  };

  const validateForm = () => {
    if (!formData.title.trim()) {
      setError('Title is required');
      return false;
    }
    if (!formData.description.trim()) {
      setError('Description is required');
      return false;
    }
    if (!formData.price || parseFloat(formData.price) <= 0) {
      setError('Please enter a valid price greater than 0');
      return false;
    }
    if (!formData.delivery_days || parseInt(formData.delivery_days) <= 0) {
      setError('Please enter valid delivery days (minimum 1)');
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setDebugInfo('');
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      const price = parseFloat(formData.price);
      const deliveryDays = parseInt(formData.delivery_days, 10);
      
      const gigData = {
        title: formData.title.trim(),
        description: formData.description.trim(),
        price: price,
        delivery_days: deliveryDays,
        tags: formData.tags.length > 0 ? formData.tags : []
      };

      // Log everything for debugging
      console.log('📤 Sending gig data:', JSON.stringify(gigData, null, 2));
      console.log('🔑 Token:', localStorage.getItem('access_token')?.substring(0, 50) + '...');
      
      setDebugInfo(`Sending: ${JSON.stringify(gigData)}`);

      const response = await api.post('/gigs', gigData);
      
      console.log('✅ Gig created:', response.data);
      setSuccess('Gig created successfully! Redirecting...');
      
      setTimeout(() => {
        navigate('/dashboard');
      }, 1500);

    } catch (error) {
      console.error('❌ Error creating gig:', error);
      
      // Detailed error logging
      let errorMessage = 'Failed to create gig';
      
      if (error.response) {
        // Server responded with error
        const status = error.response.status;
        const data = error.response.data;
        
        console.log('🔴 Status:', status);
        console.log('🔴 Response data:', data);
        
        if (status === 401) {
          errorMessage = 'Please login again to create a gig';
          setTimeout(() => navigate('/login'), 2000);
        } else if (status === 403) {
          errorMessage = 'Only freelancers can create gigs. Please switch to a freelancer account.';
        } else if (status === 400) {
          errorMessage = data?.error || data?.msg || 'Validation error';
        } else if (status === 422) {
          errorMessage = `Unprocessable entity: ${data?.error || data?.msg || JSON.stringify(data)}`;
        } else if (status === 500) {
          errorMessage = 'Server error. Please check backend logs.';
        } else {
          errorMessage = `Error ${status}: ${data?.error || data?.msg || 'Unknown error'}`;
        }
        
        setDebugInfo(`Status: ${status}, Response: ${JSON.stringify(data)}`);
      } else if (error.request) {
        errorMessage = 'Cannot connect to server. Check if backend is running.';
        setDebugInfo('No response from server');
      } else {
        errorMessage = `Error: ${error.message}`;
        setDebugInfo(`Error: ${error.message}`);
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="create-gig-page">
      <div className="container">
        <div className="create-gig-container">
          <div className="create-gig-header">
            <h1>Create a New Gig</h1>
            <p>List your service and start earning</p>
          </div>

          <form className="create-gig-form" onSubmit={handleSubmit}>
            {error && <div className="form-error">{error}</div>}
            {success && <div className="form-success">{success}</div>}
            {debugInfo && <div className="debug-info">{debugInfo}</div>}

            <div className="form-group">
              <label htmlFor="title">Gig Title *</label>
              <input
                type="text"
                id="title"
                name="title"
                value={formData.title}
                onChange={handleChange}
                required
                placeholder="e.g., I will build a stunning website"
                maxLength="200"
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="description">Description *</label>
              <textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleChange}
                required
                placeholder="Describe your service in detail..."
                rows="6"
                disabled={loading}
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="price">Price ($) *</label>
                <input
                  type="number"
                  id="price"
                  name="price"
                  value={formData.price}
                  onChange={handleChange}
                  required
                  min="1"
                  step="0.01"
                  placeholder="49.99"
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label htmlFor="delivery_days">Delivery Days *</label>
                <input
                  type="number"
                  id="delivery_days"
                  name="delivery_days"
                  value={formData.delivery_days}
                  onChange={handleChange}
                  required
                  min="1"
                  placeholder="3"
                  disabled={loading}
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="tags">Tags</label>
              <div className="tag-input-container">
                <input
                  type="text"
                  id="tags"
                  value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  onKeyDown={handleKeyPress}
                  placeholder="Add tags (e.g., web-design)"
                  disabled={loading}
                />
                <button onClick={handleAddTag} type="button" className="tag-add-btn" disabled={loading}>
                  Add Tag
                </button>
              </div>
              <div className="tags-display">
                {formData.tags.map(tag => (
                  <span key={tag} className="tag-item">
                    #{tag}
                    <button 
                      type="button" 
                      onClick={() => handleRemoveTag(tag)}
                      className="tag-remove"
                      aria-label={`Remove tag ${tag}`}
                      disabled={loading}
                    >
                      ×
                    </button>
                  </span>
                ))}
                {formData.tags.length === 0 && (
                  <span className="no-tags">No tags added yet</span>
                )}
              </div>
            </div>

            <button 
              type="submit" 
              className="submit-btn"
              disabled={loading}
            >
              {loading ? 'Creating...' : 'Create Gig'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default CreateGig;