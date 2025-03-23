const URL = 'https://script-download-backend.onrender.com';

export default async function GetPassword(ip:string){
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