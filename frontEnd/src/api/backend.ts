import axios from "axios";

export async function postData(image: File) {
    try {
        const response = await axios.post("http://127.0.0.1:8000/process-sheet-music", {
            image: image
        });
        return response.data;
    } catch (error) {
        console.error("Error fetching data:", error);
        throw error;
    }
}