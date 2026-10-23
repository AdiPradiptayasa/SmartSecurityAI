import api from "./api";

export const CameraService = {
    async status() {
        const response = await api.get("/camera/status");
        return response.data;
    }
};