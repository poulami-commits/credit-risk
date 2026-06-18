import axios from "axios";

const API = axios.create({
  baseURL: "http://localhost:8000"
});

export const getHealth = () => API.get("/health");

export const getModelInfo = () => API.get("/model/info");

export const predictLoan = (data: any) =>
  API.post("/predict", data);

export const getMetadata = () =>
  API.get("/metadata");