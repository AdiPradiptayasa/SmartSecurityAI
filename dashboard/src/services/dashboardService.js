import api from "./api";

export const DashboardService = {
    async status() {
        const response = await api.get("/dashboard");
        return response.data;
    }
};