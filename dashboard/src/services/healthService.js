import api from "./api";

export const HealthService = {
    async check() {
        const response = await api.get("/health");
        return response.data;
    }
};