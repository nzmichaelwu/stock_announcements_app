import axios from 'axios'

const API_URL = process.env.API_URL || 'http://localhost/';

export default axios.create({
  baseURL: '',
  headers: {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${localStorage.token}`,
  },
});
