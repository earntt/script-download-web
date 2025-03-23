const URL = 'https://script-download-backend.onrender.com';

export async function GetPassword(ip:string){
    const response = await fetch(
        `${URL}/api/data?ip_address=${ip}`,
        {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        }
    );
    if(!response.ok){
        throw new Error("Failed to fetch data");
    }
    return await response.json();
}

export async function GetLastest(){
    const response = await fetch(
        `${URL}/api/latest`,
        {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
        }
    );
    if(!response.ok){
        throw new Error("Failed to fetch latest data");
    }
    return await response.json().then((responseData) => {
        // The API returns { status: "success", entry: { ... data object ... } }
        // The entry object contains id, ip_address, timestamp, and data fields
        // The data field contains the parsed JSON from data_json
        if (responseData.status === "success" && responseData.entry) {
            return responseData.entry;
        } else {
            throw new Error("Invalid data format received");
        }
    });
}