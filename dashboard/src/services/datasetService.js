import api from "./api";

export const DatasetService = {
    async getAll() {
        const response = await api.get("/ai/dataset");
        return response.data;
    },

    async uploadPhotos(name, files) {
        const formData = new FormData();
        formData.append("name", name);
        for (let i = 0; i < files.length; i++) {
            formData.append("files", files[i]);
        }

        const response = await api.post("/ai/dataset/upload", formData, {
            headers: { "Content-Type": "multipart/form-data" }
        });
        return response.data;
    },

    async runEnrollment() {
        const response = await api.post("/ai/enroll/run");
        return response.data;
    }
};