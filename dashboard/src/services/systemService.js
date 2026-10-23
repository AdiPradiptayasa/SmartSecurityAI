// systemService.js — diarahkan ke /status (endpoint yang sudah kita buat & teruji)
import api from "./api";

export const SystemService = {
    async status() {
        const response = await api.get("/status");
        return response.data;
    }
};