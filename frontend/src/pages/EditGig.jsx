import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import './CreateGig.css';

const EditGig = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    price: '',
    delivery_days: '',
    tags: [],
    is_active: true,
  });
  const [tagInput, setTagInput] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchGig();
  }, [id]);

  const fetchGig = async () => {
    try {
      const response = await api.get(`/gigs/${id}`);
      const gig = response.data;
      setFormData({
        title: gig.title,
        description: gig.description,
        price: gig.price,
        delivery_days: gig.delivery_days,
        tags: gig.tags?.map(t => t.name) || [],
        is_active: gig.is_active,
      });
    } catch (error) {
      setError('Failed to load gig');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSubmitting(true);

    try {
      const gigData = {
        ...formData,
        price: parseFloat(formData.price),
        delivery_days: parseInt(formData.delivery_days),
      };
      
      await api.put(`/gigs/${id}`, gigData);
      navigate(`/gigs/${id}`);
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to update gig');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <div className="create-gig-loading">Loading gig...</div>;
  }

  return (
    <div className="create-gig-page">
      <div className="container">
        <div className="create-gig-container">
          <div className="create-gig-header">
            <h1>Edit Gig</h1>
            <p>Update your service listing</p>
          </div>

          <form className="create-gig-form" onSubmit={handleSubmit}>
            {error && <div className="form-error">{error}</div>}

            <div className="form-group">
              <label htmlFor="title">Gig Title</label>
              <input
                type="text"
                id="title"
                name="title"
                value={formData.title}
                onChange={handleChange}
                required
                maxLength="200"
              />
            </div>

            <div className="form-group">
              <label htmlFor="description">Description</label>
              <textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleChange}
                required
                rows="6"
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="price">Price ($)</label>
                <input
                  type="number"
                  id="price"
                  name="price"
                  value={formData.price}
                  onChange={handleChange}
                  required
                  min="1"
                  step="0.01"
                />
              </div>

              <div className="form-group">
                <label htmlFor="delivery_days">Delivery Days</label>
                <input
                  type="number"
                  id="delivery_days"
                  name="delivery_days"
                  value={formData.delivery_days}
                  onChange={handleChange}
                  required
                  min="1"
                />
              </div>
            </div>

            <div className="form-group">
              <label>Tags</label>
              <div className="tag-input-container">
                <input
                  type="text"
                  value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  placeholder="Add tags"
                  onKeyPress={(e) => e.key === 'Enter' && handleAddTag(e)}
                />
                <button onClick={handleAddTag} type="button" className="tag-add-btn">
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
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            </div>

            <div className="form-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  name="is_active"
                  checked={formData.is_active}
                  onChange={handleChange}
                />
                Active (visible to clients)
              </label>
            </div>

            <button 
              type="submit" 
              className="submit-btn"
              disabled={submitting}
            >
              {submitting ? 'Updating...' : 'Update Gig'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default EditGig;