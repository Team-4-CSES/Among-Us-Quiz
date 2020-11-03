import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:9000/api",
});

export const insertQuiz = (payload) => api.post(`/quiz`, payload);
export const getAllQuizzes = () => api.get(`/quizzes`);
export const updateQuizById = (id, payload) => api.put(`/quiz/${id}`, payload);
export const deleteQuizById = (id) => api.delete(`/quiz/${id}`);
export const getQuizById = (id) => api.get(`/quiz/${id}`);

const apis = {
  insertQuiz,
  getAllQuizzes,
  updateQuizById,
  deleteQuizById,
  getQuizById,
};

export default apis;
