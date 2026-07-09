import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import './MyOrders.css';

const MyOrders = () => {
  const { user } = useAuth();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const response = await api.get('/orders');
      setOrders(response.data.orders || []);
    } catch (error) {
      console.error('Error fetching orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCancelOrder = async (orderId) => {
    if (!window.confirm('Are you sure you want to cancel this order?')) return;

    try {
      await api.delete(`/orders/${orderId}`);
      await fetchOrders();
    } catch (error) {
      alert(error.response?.data?.error || 'Failed to cancel order');
    }
  };

  const filteredOrders = orders.filter(order => {
    if (filter === 'all') return true;
    return order.status === filter;
  });

  const getStatusBadge = (status) => {
    const badges = {
      pending: 'badge-warning',
      in_progress: 'badge-info',
      completed: 'badge-success',
      cancelled: 'badge-danger'
    };
    return badges[status] || 'badge-default';
  };

  if (loading) {
    return <div className="orders-loading">Loading your orders...</div>;
  }

  return (
    <div className="orders-page">
      <div className="container">
        <div className="orders-header">
          <h1>My Orders</h1>
          <div className="orders-filter">
            <button 
              className={filter === 'all' ? 'filter-active' : ''}
              onClick={() => setFilter('all')}
            >
              All
            </button>
            <button 
              className={filter === 'pending' ? 'filter-active' : ''}
              onClick={() => setFilter('pending')}
            >
              Pending
            </button>
            <button 
              className={filter === 'in_progress' ? 'filter-active' : ''}
              onClick={() => setFilter('in_progress')}
            >
              In Progress
            </button>
            <button 
              className={filter === 'completed' ? 'filter-active' : ''}
              onClick={() => setFilter('completed')}
            >
              Completed
            </button>
          </div>
        </div>

        {filteredOrders.length === 0 ? (
          <div className="orders-empty">
            <p>No orders found</p>
          </div>
        ) : (
          <div className="orders-list">
            {filteredOrders.map(order => (
              <div key={order.id} className="order-card">
                <div className="order-card-header">
                  <div className="order-gig-info">
                    <h3 className="order-gig-title">{order.gig_title || 'Untitled Gig'}</h3>
                    <span className={`order-status-badge ${getStatusBadge(order.status)}`}>
                      {order.status.replace('_', ' ')}
                    </span>
                  </div>
                  <div className="order-price">${order.total_price}</div>
                </div>

                <div className="order-card-body">
                  {order.requirements && (
                    <div className="order-requirements">
                      <strong>Requirements:</strong>
                      <p>{order.requirements}</p>
                    </div>
                  )}
                  <div className="order-meta">
                    <span>Ordered: {new Date(order.created_at).toLocaleDateString()}</span>
                    {order.review && (
                      <span className="order-review">
                        ⭐ {order.review.rating}/5 - {order.review.comment}
                      </span>
                    )}
                  </div>
                </div>

                <div className="order-card-footer">
                  {order.status === 'pending' && (
                    <button 
                      className="btn-cancel"
                      onClick={() => handleCancelOrder(order.id)}
                    >
                      Cancel Order
                    </button>
                  )}
                  {order.status === 'completed' && !order.review && (
                    <button className="btn-review">
                      Leave Review
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MyOrders;